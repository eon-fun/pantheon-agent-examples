import asyncio

# import logging # Commented out
import sys
from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from ray import serve
from telethon import TelegramClient, events
from telethon.errors import (
    AuthKeyError,
    ChannelPrivateError,
    ChatAdminRequiredError,
    FloodWaitError,
    SessionPasswordNeededError,
    UserNotParticipantError,
)

from .client import TelethonClientManager, get_telethon_client_service
from .data_processor import initialize_data_processing, process_new_message

load_dotenv()

# TELEGRAM_PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER")
# TARGET_CHAT_ID_STR = os.getenv("TARGET_CHAT_ID")
TELEGRAM_PHONE_NUMBER = ""
TARGET_CHAT_ID = ""

# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper() # Commented out as logger is removed

# logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__) # Commented out

# if not TELEGRAM_PHONE_NUMBER:
# print("CRITICAL: TELEGRAM_PHONE_NUMBER environment variable is not set.", file=sys.stderr)
# exit(1)
# if not TARGET_CHAT_ID_STR: # TARGET_CHAT_ID is now directly an int
# print("CRITICAL: TARGET_CHAT_ID environment variable is not set.", file=sys.stderr)
# exit(1)

# try:
# TARGET_CHAT_ID: Union[int, str] = int(TARGET_CHAT_ID_STR) # TARGET_CHAT_ID is now directly an int
# print(f"INFO: Target chat ID interpreted as integer: {TARGET_CHAT_ID}")
# except ValueError:
# TARGET_CHAT_ID = TARGET_CHAT_ID_STR
# print(f"INFO: Target chat ID interpreted as string/username: {TARGET_CHAT_ID}")
print(f"INFO: Using hardcoded Target chat ID: {TARGET_CHAT_ID}")
print(f"INFO: Using hardcoded Telegram Phone Number: {TELEGRAM_PHONE_NUMBER}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("DEBUG: lifespan - Start", file=sys.stderr)
    print("INFO: Agent lifespan start: Initializing data processing backend...")
    try:
        print("DEBUG: lifespan - Calling initialize_data_processing...", file=sys.stderr)
        await initialize_data_processing()
        print("DEBUG: lifespan - initialize_data_processing completed.", file=sys.stderr)
        app.state.data_processing_initialized = True
        print("DEBUG: lifespan - app.state.data_processing_initialized = True", file=sys.stderr)
        print("INFO: Data processing backend initialized successfully.")
    except Exception as e:
        print(f"DEBUG: lifespan - Failed to initialize data processing backend: {e}", file=sys.stderr)
        print(f"CRITICAL: Failed to initialize data processing backend: {e}", file=sys.stderr)
        app.state.data_processing_initialized = False
        print("DEBUG: lifespan - app.state.data_processing_initialized = False", file=sys.stderr)
    yield
    print("DEBUG: lifespan - End, cleaning up resources...", file=sys.stderr)
    print("INFO: Agent lifespan end: Cleaning up resources (if any)...")


app = FastAPI(title="Telegram Listener Agent", lifespan=lifespan)


@serve.deployment(
    name="TelegramListenerAgentDeployment",
)
@serve.ingress(app)
class TelegramListenerAgent(BaseAgent):
    def __init__(self):
        print("DEBUG: TelegramListenerAgent.__init__ - Start", file=sys.stderr)
        print("INFO: Initializing TelegramListenerAgent instance...")
        data_processing_initialized = getattr(app.state, "data_processing_initialized", False)
        print(
            f"DEBUG: TelegramListenerAgent.__init__ - app.state.data_processing_initialized = {data_processing_initialized}",
            file=sys.stderr,
        )
        if not data_processing_initialized:
            print(
                "ERROR: Data processing backend failed to initialize. Agent may not function correctly.",
                file=sys.stderr,
            )

        self.telethon_manager: TelethonClientManager = get_telethon_client_service()
        self.client: TelegramClient | None = None
        self.listener_task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self.phone_number = TELEGRAM_PHONE_NUMBER
        self.target_chat_id = TARGET_CHAT_ID
        print(f"INFO: Agent instance created for phone: {self.phone_number}, target chat: {self.target_chat_id}")
        print("DEBUG: TelegramListenerAgent.__init__ - End", file=sys.stderr)

    async def _message_handler(self, event: events.NewMessage.Event):
        """Callback function passed to Telethon, calls the data processor."""
        if self.client and self.client.is_connected():  # Added check for connection
            asyncio.create_task(self._process_event_safely(event, self.client))
        else:
            print(
                f"WARNING: Telegram client not ready in _message_handler for event from chat {event.chat_id}. Attempting to get client.",
                file=sys.stderr,
            )
            try:
                current_client = await self._get_telethon_client()
                if current_client and current_client.is_connected():
                    self.client = current_client
                    asyncio.create_task(self._process_event_safely(event, self.client))
                else:
                    print(
                        f"ERROR: Failed to get a connected Telegram client in _message_handler for event from chat {event.chat_id}. Message may not be processed.",
                        file=sys.stderr,
                    )
            except Exception as e:
                print(f"ERROR: Exception while trying to get client in _message_handler: {e}", file=sys.stderr)

    async def _process_event_safely(self, event: events.NewMessage.Event, telegram_client: TelegramClient):
        """Wraps the data processor call in error handling."""
        try:
            await process_new_message(event, telegram_client)
        except Exception as e:
            print(f"ERROR: Error processing message {getattr(event.message, 'id', 'N/A')}: {e}", file=sys.stderr)

    async def _get_telethon_client(self) -> TelegramClient:
        """Retrieves and connects the Telethon client using the manager."""
        print(f"INFO: Attempting to get Telethon client for {self.phone_number}...")
        try:
            client = await self.telethon_manager._get_client(self.phone_number)
            if not client.is_connected():
                print("INFO: Client not connected, attempting connection...")
                await client.connect()
                if not client.is_connected():
                    raise ConnectionError("Failed to connect Telethon client after retrieval.")
            print(f"INFO: Successfully obtained and connected client for {self.phone_number}.")
            return client
        except AuthKeyError:
            print(
                f"ERROR: Authentication key error for {self.phone_number}. Session might be invalid. Please re-authenticate.",
                file=sys.stderr,
            )
            raise HTTPException(status_code=401, detail="Telegram Auth Key Error. Re-authentication required.")
        except Exception as e:
            print(f"ERROR: Failed to get or connect Telethon client for {self.phone_number}: {e}", file=sys.stderr)
            raise HTTPException(status_code=503, detail=f"Error initializing Telegram client: {e}")

    async def _run_listener_loop(self):
        """The main listener loop running in a background task."""
        while not self._stop_event.is_set():
            try:
                if self.client is None or not self.client.is_connected():
                    print("INFO: Client is None or not connected. Attempting to establish connection...")
                    self.client = await self._get_telethon_client()

                    if not await self.client.is_user_authorized():
                        print(
                            f"ERROR: User {self.phone_number} is not authorized. Stopping listener. Please complete login process.",
                            file=sys.stderr,
                        )
                        await self.client.disconnect()
                        self.client = None
                        self._stop_event.set()
                        break

                    print(f"INFO: Client authorized. Adding event handler for chat: {self.target_chat_id}")
                    try:
                        self.client.remove_event_handler(self._message_handler)
                        print("DEBUG: Removed existing message handler (if any).")
                    except ValueError:
                        print("DEBUG: No existing message handler to remove.")

                    self.client.add_event_handler(self._message_handler, events.NewMessage(chats=self.target_chat_id))
                    print("INFO: Event handler added. Listener running.")

                await asyncio.sleep(5)
                if not self.client.is_connected():
                    print(
                        "WARNING: Client disconnected unexpectedly. Will attempt reconnect in next loop iteration.",
                        file=sys.stderr,
                    )  # Was logger.warning
                    self.client = None
                    continue

            except SessionPasswordNeededError:
                print(
                    f"ERROR: 2FA password needed for {self.phone_number}. Stopping listener.", file=sys.stderr
                )  # Was logger.error
                self._stop_event.set()
            except (ChannelPrivateError, ChatAdminRequiredError, UserNotParticipantError) as e:
                print(
                    f"ERROR: Permission Error accessing chat {self.target_chat_id}: {e}. Stopping listener.",
                    file=sys.stderr,
                )  # Was logger.error
                self._stop_event.set()
            except FloodWaitError as e:
                print(f"WARNING: Flood wait encountered: {e.seconds} seconds. Sleeping...", file=sys.stderr)
                await asyncio.sleep(e.seconds + 5)
            except AuthKeyError:
                print(
                    f"ERROR: Authentication key error during listener loop for {self.phone_number}. Session invalid. Stopping listener.",
                    file=sys.stderr,
                )
                self._stop_event.set()
            except ConnectionError as e:
                print(
                    f"ERROR: Connection error during listener loop: {e}. Retrying connection shortly...",
                    file=sys.stderr,
                )
                if self.client:
                    try:
                        self.client.remove_event_handler(self._message_handler)
                    except:
                        pass
                    await self.client.disconnect()
                self.client = None
                await asyncio.sleep(15)
            except Exception as e:
                print(f"ERROR: An unexpected error occurred in listener loop: {e}", file=sys.stderr)
                if self.client and self.client.is_connected():
                    try:
                        self.client.remove_event_handler(self._message_handler)
                    except:
                        pass
                    await self.client.disconnect()
                self.client = None
                print("INFO: Sleeping after unexpected error before potentially retrying...")
                await asyncio.sleep(30)

        print("INFO: Listener loop finishing.")
        if self.client and self.client.is_connected():
            print("INFO: Disconnecting client...")
            try:
                self.client.remove_event_handler(self._message_handler)
            except:
                pass
            await self.client.disconnect()
            print("INFO: Client disconnected.")
        self.client = None
        self.listener_task = None
        print("INFO: Listener task cleanup complete.")

    @app.post("/control/start", status_code=202)
    async def start_listening(self):
        print("DEBUG: /control/start - Request received", file=sys.stderr)
        data_processing_initialized = getattr(app.state, "data_processing_initialized", False)
        print(
            f"DEBUG: /control/start - app.state.data_processing_initialized = {data_processing_initialized}",
            file=sys.stderr,
        )
        if not data_processing_initialized:
            print("DEBUG: /control/start - Raising 503 due to data processing not initialized", file=sys.stderr)
            raise HTTPException(status_code=503, detail="Data processing backend not initialized.")

        if self.listener_task and not self.listener_task.done():
            print("WARNING: Start request received but listener task is already running.", file=sys.stderr)
            return {"status": "Listener already running."}

        print("INFO: Received request to start listener...")
        self._stop_event.clear()
        self.listener_task = asyncio.create_task(self._run_listener_loop())
        print("INFO: Listener task created.")
        return {"status": "Listener start requested."}

    @app.post("/control/stop", status_code=202)
    async def stop_listening(self):
        if not self.listener_task or self.listener_task.done():
            print(
                "WARNING: Stop request received but listener task is not running or already finished.", file=sys.stderr
            )
            return {"status": "Listener not running."}

        print("INFO: Received request to stop listener...")
        self._stop_event.set()

        await asyncio.sleep(1)

        return {"status": "Listener stop requested."}

    @app.get("/control/status")
    async def get_status(self):
        """Checks the status of the listener task and client connection."""
        task_running = self.listener_task and not self.listener_task.done()
        client_connected = self.client is not None and self.client.is_connected()

        status = "stopped"
        if task_running:
            status = "running" if not self._stop_event.is_set() else "stopping"
        elif not task_running and self._stop_event.is_set():
            status = "stopped"

        return {
            "status": status,
            "client_connected": client_connected,
            "phone": self.phone_number,
            "target_chat": self.target_chat_id,
        }


def get_agent(agent_args: dict):
    return TelegramListenerAgent.bind(**agent_args)


# telegram_listener_agent_deployment = build_telegram_listener_agent regwgrgrwergweg comment


if __name__ == "__main__":
    # print("INFO: Starting Telegram Listener Agent locally using Ray Serve...")
    # deployment = get_agent({})
    serve.run(app, route_prefix="/")

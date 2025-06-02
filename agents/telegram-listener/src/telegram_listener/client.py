## TODO: Вынести логику клиента в отдельную библиотеку
from typing import Optional

from redis_client.main import RedisDB, get_redis_db
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

HARDCODED_API_ID = 2
HARDCODED_API_HASH = ""
HARDCODED_SESSION_STRING = ""
DEVICE_MODEL = "Desktop"
SYSTEM_VERSION = "Windows 10"
APP_VERSION = "1.0.0"
FLOOD_SLEEP_THRESHOLD = 60


class TelethonClientManager:
    """
    A manager class for handling TelegramClient instances with Redis-based session storage.
    """

    def __init__(self, redis_service: RedisDB):
        """
        Initialize the manager with the RedisDB service.

        :param redis_service: Instance of RedisDB for session storage.
        """
        self.redis = redis_service

    async def create_client(self, phone_number: str, api_id: int, api_hash: str) -> TelegramClient:
        """
        Create a new TelegramClient and save it to Redis.

        :param phone_number: User's phone number (used as the key in Redis).
        :param api_id: Telegram API ID.
        :param api_hash: Telegram API Hash.
        :return: An instance of TelegramClient.
        """
        existing_session = self.redis.get(f"telegram_session:{phone_number}")
        if existing_session:
            raise ValueError(f"Session for {phone_number} already exists.")

        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()

        # Save session to Redis as an empty StringSession initially
        self._save_session(phone_number, client)
        return client

    async def start_login(self, phone_number: str) -> str:
        """
        Start the login process by sending a code to the user's phone number.
        """
        # logger.info(f"Initializing login process for phone number: {phone_number}...")
        print(f"INFO: Initializing login process for phone number: {phone_number}...")

        session_key = f"telegram_session:{phone_number}"
        if self.redis.get(session_key):
            self.redis.delete(session_key)
            # logger.info(f"Old session for {phone_number} deleted.")
            print(f"INFO: Old session for {phone_number} deleted.")

        try:
            app_key = f"titan:{phone_number}"
            app_data = self.redis.get(app_key)
            if not app_data:
                raise ValueError(f"API data for {phone_number} not found in Redis.")

            app_data = eval(app_data.decode()) if isinstance(app_data, bytes) else app_data
            api_id = int(app_data["api_id"])
            api_hash = app_data["api_hash"]

            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()

            code_hash = await client.send_code_request(phone_number)
            self.redis.set(session_key, client.session.save())
            return code_hash.phone_code_hash
        except Exception as e:
            print(f"ERROR: Error during login process for {phone_number}: {e}")
            raise RuntimeError(f"Failed to start login for {phone_number}: {e}")

    async def complete_login(
        self, phone_number: str, phone_code: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """
        Complete the login process by verifying the code or entering the 2FA password.

        :param phone_number: User's phone number.
        :param phone_code: Code received from Telegram.
        :param password: Password for 2FA (if required).
        """
        client = self._get_client(phone_number)

        try:
            if phone_code:
                await client.sign_in(phone_number, phone_code)
            if password:
                await client.sign_in(password=password)
            self._save_session(phone_number, client)
        except SessionPasswordNeededError:
            raise ValueError("Password is required for 2FA login.")
        except Exception as e:
            raise RuntimeError(f"Failed to complete login for {phone_number}: {e}")

    async def disconnect_client(self, phone_number: str):
        """
        Disconnect the client and remove the session from Redis.

        :param phone_number: User's phone number.
        """
        client = self._get_client(phone_number)
        await client.disconnect()
        self.redis.delete(f"telegram_session:{phone_number}")

    def get_client_session_string(self, phone_number: str) -> str:
        """
        Get the session string for a specific phone number.

        :param phone_number: User's phone number.
        :return: Serialized session string.
        """
        session_string = self.redis.get(f"telegram_session:{phone_number}")
        if not session_string:
            raise ValueError(f"Session for {phone_number} not found.")
        return session_string

    def _save_session(self, phone_number: str, client: TelegramClient):
        """
        Save the client's session to Redis.

        :param phone_number: User's phone number.
        :param client: TelegramClient instance.
        """
        session_string = client.session.save()
        self.redis.set(f"telegram_session:{phone_number}", session_string)

    async def _get_client(self, phone_number: str) -> TelegramClient:
        """
        Retrieve a client using hardcoded session string, API ID, and API Hash.
        The phone_number argument is kept for interface compatibility but is mostly ignored
        for client instantiation when using hardcoded values.
        """
        print(
            f"INFO: Using hardcoded Telethon client. Provided phone_number ('{phone_number}') is ignored for client creation with hardcoded session."
        )

        client = TelegramClient(
            StringSession(HARDCODED_SESSION_STRING),
            HARDCODED_API_ID,
            HARDCODED_API_HASH,
            device_model=DEVICE_MODEL,
            system_version=SYSTEM_VERSION,
            app_version=APP_VERSION,
            flood_sleep_threshold=FLOOD_SLEEP_THRESHOLD,
        )

        if not client.is_connected():
            await client.connect()

        if not await client.is_user_authorized():
            print("ERROR: Hardcoded session is not authorized. Please ensure the session string is valid and active.")

        return client


def get_telethon_client_service() -> TelethonClientManager:
    # TODO: Заменить хардкод на получение настроек из get_settings()

    redis_service = get_redis_db()

    return TelethonClientManager(redis_service=redis_service)

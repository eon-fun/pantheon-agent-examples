import ray
import asyncio
import json
from telethon import TelegramClient, events, functions
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberUnoccupiedError
from telethon.tl.types import Message, PeerUser, PeerChannel, PeerChat, InputPeerEmpty
from services.ai_tools.openai_client import send_openai_request
from database.redis.redis_client import RedisDB

# Configuration
API_ID = "26012476"
API_HASH = "d0ba6cd225c5dea4d2f7eb717adbeaac"
SESSION_NAME = "my_telegram_session"
REDIS_MESSAGES_KEY = "telegram_messages"
BOT_COMMAND = "/summary"

PROMPT = (
    "You are an assistant summarizing messages in a chat. "
    "Your task is to create a brief summary of what each user discussed without answering any questions. "
    "For example: \n"
    "@username mentioned something about topic X.\n"
    "@another_user brought up another topic Y.\n"
    "Also note if someone was mentioned or replied to in the chat and include the chat name. "
    "Do not provide solutions, just summarize the content of the messages concisely."
)


@ray.remote
class MessageProcessor:
    def __init__(self):
        self.db = None

    def initialize(self):
        """Initialize Redis connection"""
        if not self.db:
            self.db = RedisDB()

    async def process_message(self, message_data):
        """Process and store message in Redis"""
        try:
            if not self.db:
                self.initialize()

            self.db.add_to_sorted_set(
                REDIS_MESSAGES_KEY,
                int(message_data["timestamp"]),
                json.dumps(message_data)
            )
            print(f"✅ Message saved from chat '{message_data['chat_name']}': {message_data['text'][:50]}...")

        except Exception as e:
            print(f"❌ Error processing message: {e}")

    async def update_read_messages(self, read_messages_data):
        """Update Redis with read message information"""
        try:
            if not self.db:
                self.initialize()

            messages = self.db.get_sorted_set(REDIS_MESSAGES_KEY)
            if not messages:
                return

            updated_messages = []
            for msg in messages:
                msg_data = json.loads(msg)
                chat_id = msg_data["chat_id"]
                message_id = int(msg_data["id"])

                # Проверяем, является ли сообщение прочитанным
                is_read = any(
                    chat_id == chat_info["chat_id"] and message_id <= chat_info["max_id"]
                    for chat_info in read_messages_data
                )

                # Оставляем НЕпрочитанные сообщения
                if not is_read:
                    updated_messages.append(msg)
                    print(f"✅ Keeping unread message ID {message_id} from chat {chat_id}")
                else:
                    print(f"🗑 Removing read message ID {message_id} from chat {chat_id}")

            # Обновляем Redis только если были изменения
            if len(updated_messages) != len(messages):
                print(f"📊 Updating Redis: {len(messages)} -> {len(updated_messages)} messages")
                self.db.delete(REDIS_MESSAGES_KEY)
                for msg in updated_messages:
                    msg_data = json.loads(msg)
                    self.db.add_to_sorted_set(
                        REDIS_MESSAGES_KEY,
                        int(msg_data["timestamp"]),
                        msg
                    )

        except Exception as e:
            print(f"❌ Error updating read messages: {e}")

    async def generate_summary(self):
        """Generate summary from stored messages"""
        try:
            if not self.db:
                self.initialize()

            messages = self.db.get_sorted_set(REDIS_MESSAGES_KEY)
            if not messages:
                return "No messages to process."

            combined_text = "\n".join([
                f"[{json.loads(msg)['chat_name']}] {json.loads(msg)['sender_username']} {json.loads(msg)['action']}: {json.loads(msg)['text']}"
                for msg in messages
            ])

            self.db.delete(REDIS_MESSAGES_KEY)

            messages = [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": combined_text}
            ]

            summary = await send_openai_request(messages)
            return summary.strip()

        except Exception as e:
            return f"Error processing summary: {e}"


async def get_read_messages_data(client):
    """Get information about read messages from Telegram"""
    try:
        dialogs = await client(functions.messages.GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=100,
            hash=0
        ))

        return [
            {
                "chat_id": (
                    d.peer.user_id if isinstance(d.peer, PeerUser)
                    else d.peer.channel_id if isinstance(d.peer, PeerChannel)
                    else d.peer.chat_id if isinstance(d.peer, PeerChat)
                    else None
                ),
                "max_id": d.read_inbox_max_id
            }
            for d in dialogs.dialogs
        ]
    except Exception as e:
        print(f"❌ Error getting read messages data: {e}")
        return []


async def main():
    # Initialize Ray
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)
        print("Ray initialized successfully!")

    # Initialize processor
    processor = MessageProcessor.remote()
    processor.initialize.remote()

    # Initialize Telegram client
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

    @client.on(events.NewMessage(pattern=BOT_COMMAND))
    async def handle_summary_command(event):
        """Handle /summary command and send summary"""
        try:
            await event.respond("⏳ Generating summary, please wait...")

            # Get read messages data first
            read_messages_data = await get_read_messages_data(client)

            # Update read messages status
            await processor.update_read_messages.remote(read_messages_data)

            # Generate summary
            summary_future = processor.generate_summary.remote()
            summary = await asyncio.to_thread(ray.get, summary_future)

            await event.respond(f"📋 Summary:\n{summary}")
        except Exception as e:
            await event.respond(f"❌ Error generating summary: {e}")

    @client.on(events.NewMessage)
    async def handle_new_message(event):
        """Process new messages"""
        try:
            if not event.text or event.message.out:
                return

            sender = await event.get_sender()
            chat = await event.get_chat()

            chat_name = chat.title if hasattr(chat, 'title') and chat.title else "Private Chat"
            username = sender.username if sender and sender.username else None
            name = f"@{username}" if username else (sender.first_name if sender and sender.first_name else "Unknown")

            action = "wrote"
            if event.message.mentioned:
                action = "mentioned"
            elif event.message.reply_to:
                action = "replied"

            message_data = {
                "id": str(event.message.id),
                "text": event.text,
                "sender_username": name,
                "action": action,
                "chat_name": chat_name,
                "chat_id": chat.id,
                "timestamp": event.message.date.timestamp()
            }

            await processor.process_message.remote(message_data)

        except Exception as e:
            print(f"❌ Error handling message: {e}")

    try:
        print("🚀 Starting Telethon client")
        await client.connect()
        if not await client.is_user_authorized():
            print("⏳ Authentication required")
            phone = input("Enter your phone number: ").strip()
            await client.send_code_request(phone)
            code = input("Enter SMS code: ").strip()
            try:
                await client.sign_in(phone=phone, code=code)
            except SessionPasswordNeededError:
                password = input("Enter your cloud password (2FA): ").strip()
                await client.sign_in(password=password)

        print("✅ Successfully connected!")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Startup error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
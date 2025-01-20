import ray
import json
from telethon import functions, types
from telethon.tl.types import InputPeerEmpty, PeerUser, PeerChannel, PeerChat
from database.redis.redis_client import RedisDB  # Ваш клиент Redis
from services.ai_tools.openai_client import send_openai_request  # Ваш OpenAI клиент

TELEGRAM_PROMPT = """
You are an assistant summarizing messages in a chat. 
Your task is to create a brief summary of what each user discussed without answering any questions. 
For example: 
@username mentioned something about topic X.
@another_user brought up another topic Y.
Also note if someone was mentioned or replied to in the chat and include the chat name. 
Do not provide solutions, just summarize the content of the messages concisely.
"""


@ray.remote
class MessageProcessor:
    def __init__(self):
        self.db = RedisDB()
        print("✅ MessageProcessor initialized")

    async def process_message(self, message_data):
        """Processes a message and saves it to Redis."""
        try:
            if not message_data:
                print("⚠️ Empty message data received. Skipping...")
                return

            # Проверяем данные перед добавлением
            print(f"🔍 Processing message data: {message_data}")

            # Добавляем сообщение в Redis
            self.db.add_to_sorted_set("telegram_messages", int(message_data["timestamp"]), json.dumps(message_data))
            print(f"✅ Message saved to Redis: {message_data['text'][:50]}...")
        except Exception as e:
            print(f"❌ Error processing message: {e}")

    async def update_read_messages(self, read_messages_data):
        """Updates messages as read in Redis."""
        try:
            print("🔄 Updating read messages...")
            messages = self.db.get_sorted_set("telegram_messages")
            if not messages:
                print("ℹ️ No messages to update")
                return

            updated_messages = []
            for msg in messages:
                msg_data = json.loads(msg)
                is_read = any(
                    msg_data["chat_id"] == chat_info["chat_id"] and
                    int(msg_data["id"]) <= chat_info["max_id"]
                    for chat_info in read_messages_data
                )
                if not is_read:
                    updated_messages.append(msg)

            if len(updated_messages) != len(messages):
                self.db.delete("telegram_messages")
                for msg in updated_messages:
                    msg_data = json.loads(msg)
                    self.db.add_to_sorted_set("telegram_messages", int(msg_data["timestamp"]), msg)
            print("✅ Read messages updated")
        except Exception as e:
            print(f"❌ Error updating read messages: {e}")

    async def generate_summary(self):
        """Generates a summary of messages."""
        try:
            print("🔄 Generating summary...")
            messages = self.db.get_sorted_set("telegram_messages")
            if not messages:
                print("ℹ️ No messages to summarize")
                return "No messages to process."

            combined_text = "\n".join([
                f"[{json.loads(msg)['chat_name']}] {json.loads(msg)['sender_username']} {json.loads(msg)['action']}: {json.loads(msg)['text']}"
                for msg in messages
            ])

            self.db.delete("telegram_messages")

            messages = [{"role": "system", "content": TELEGRAM_PROMPT}, {"role": "user", "content": combined_text}]

            summary = await send_openai_request(messages)
            print("✅ Summary generated")
            return summary.strip()
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return f"Error processing summary: {e}"

    async def handle_new_message(self, event):
        """Handles new messages, checking mentions and replies."""
        try:
            if not event.text or event.message.out:
                return

            sender = await event.get_sender()
            chat = await event.get_chat()

            sender_username = "Unknown User"
            if sender is not None:
                sender_username = f"@{sender.username}" if sender.username else sender.first_name

            message_data = {
                "id": str(event.message.id),
                "text": event.text,
                "sender_username": sender_username,
                "action": "mentioned" if event.message.mentioned else "replied" if event.message.reply_to else "wrote",
                "chat_name": chat.title if hasattr(chat, 'title') and chat.title else "Private Chat",
                "chat_id": chat.id,
                "timestamp": event.message.date.timestamp()
            }

            await self.process_message(message_data)
        except Exception as e:
            print(f"❌ Error handling message: {e}")


async def get_read_messages_data(client):
    """Fetch information about read messages from Telegram."""
    try:
        dialogs = await client(functions.messages.GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),  # Исправлено: корректное использование InputPeerEmpty
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
        print(f"❌ Error fetching read messages: {e}")
        return []

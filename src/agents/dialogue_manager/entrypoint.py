import json

from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent.ray_entrypoint import BaseAgent
from telethon import events

from dialogue_manager.config import db, get_settings, telethon_client
from dialogue_manager.src.prompts import AI_PROMPT
from dialogue_manager.src.commands import telethon_auth, get_read_messages_data
from services.ai_connectors.openai_client import send_openai_request  # Вынести в либу


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class DialogueManager(BaseAgent):
    @app.post("/{goal}")
    def handle(self, goal: str, plan: dict | None = None):
        await telethon_auth()

        @telethon_client.on(events.NewMessage(pattern="/summary"))
        async def handle_summary_command(event):
            """Handle the /summary command."""
            try:
                await event.respond("⏳ Generating summary, please wait...")
                read_messages_data = await get_read_messages_data(telethon_client)
                await self.update_read_messages(read_messages_data)
                summary = await self.generate_summary()
                await event.respond(f"📋 Summary:\n{summary}")
            except Exception as e:
                print(f"❌ Error generating summary: {e}")
                await event.respond("❌ An error occurred while generating the summary.")

    async def process_message(self, message_data):
        try:
            if not message_data:
                print("⚠️ Empty message data received. Skipping...")
                return

            print(f"🔍 Processing message data: {message_data}")

            db.add_to_sorted_set(get_settings().REDIS_MESSAGES_KEY, int(message_data["timestamp"]), json.dumps(message_data))
        except Exception as e:
            print(f"❌ Error processing message: {e}")

    async def update_read_messages(self, read_messages_data):
        try:
            print("🔄 Updating read messages...")
            messages = db.get_sorted_set(get_settings().REDIS_MESSAGES_KEY)
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
                db.delete(get_settings().REDIS_MESSAGES_KEY)
                for msg in updated_messages:
                    msg_data = json.loads(msg)
                    db.add_to_sorted_set(get_settings().REDIS_MESSAGES_KEY, int(msg_data["timestamp"]), msg)
            print("✅ Read messages updated")
        except Exception as e:
            print(f"❌ Error updating read messages: {e}")

    async def generate_summary(self):
        try:
            print("🔄 Generating summary...")
            messages = db.get_sorted_set(get_settings().REDIS_MESSAGES_KEY)
            if not messages:
                print("ℹ️ No messages to summarize")
                return "No messages to process."

            combined_text = "\n".join([
                f"[{json.loads(msg)['chat_name']}] {json.loads(msg)['sender_username']} {json.loads(msg)['action']}: {json.loads(msg)['text']}"
                for msg in messages
            ])

            db.delete(get_settings().REDIS_MESSAGES_KEY)

            messages = [{"role": "system", "content": AI_PROMPT}, {"role": "user", "content": combined_text}]

            summary = await send_openai_request(messages)
            print("✅ Summary generated")
            return summary.strip()
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return f"Error processing summary: {e}"

    async def handle_new_message(self, event):
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


app = DialogueManager.bind(get_settings())

if __name__ == "__main__":
    serve.run(app, route_prefix="/")

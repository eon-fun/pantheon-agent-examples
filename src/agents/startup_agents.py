import ray
import asyncio
from telethon import TelegramClient, events, functions
from telethon.errors import SessionPasswordNeededError
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.enums import ParseMode
from telethon.tl.types import InputPeerEmpty

from simple_ai_agents.ai_dialogue_manager.ray_dialogue_manager import MessageProcessor
from simple_ai_agents.ai_twitter_summary.ray_twitter_summary import TweetProcessor
from simple_ai_agents.ai_avatar.ray_avatar import AvatarAgent

# Configuration
API_ID = "26012476"
API_HASH = "d0ba6cd225c5dea4d2f7eb717adbeaac"
TELEGRAM_BOT_TOKEN = "8039253205:AAEFwlG0c2AmhwIXnqC9Q5TsBo_x-7jM2a0"
SESSION_NAME = "my_telegram_session"
TELEGRAM_CHANNEL_ID = "@panteoncryptonews"


class AgentOrchestrator:
    def __init__(self):
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)
            print("✅ Ray initialized successfully!")

        self.message_processor = MessageProcessor.remote()
        self.tweet_processor = TweetProcessor.remote()
        self.avatar_agent = AvatarAgent.remote()
        self.telethon_client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
        self.aiogram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()

    async def get_read_messages_data(self):
        """Fetch information about read messages from Telegram."""
        try:
            dialogs = await self.telethon_client(functions.messages.GetDialogsRequest(
                offset_date=None,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=100,
                hash=0
            ))
            return [
                {
                    "chat_id": (
                        d.peer.user_id if hasattr(d.peer, "user_id")
                        else d.peer.channel_id if hasattr(d.peer, "channel_id")
                        else d.peer.chat_id if hasattr(d.peer, "chat_id")
                        else None
                    ),
                    "max_id": d.read_inbox_max_id,
                }
                for d in dialogs.dialogs
            ]
        except Exception as e:
            print(f"❌ Error fetching read messages: {e}")
            return []

    async def setup_handlers(self):
        """Setup command handlers for both Telethon and Aiogram bots."""
        print("🔧 Setting up handlers...")

        @self.telethon_client.on(events.NewMessage(pattern="/summary"))
        async def handle_summary_command(event):
            """Handle the /summary command."""
            try:
                await event.respond("⏳ Generating summary, please wait...")
                read_messages_data = await self.get_read_messages_data()
                await self.message_processor.update_read_messages.remote(read_messages_data)
                summary = await self.message_processor.generate_summary.remote()
                await event.respond(f"📋 Summary:\n{summary}")
            except Exception as e:
                print(f"❌ Error generating summary: {e}")
                await event.respond("❌ An error occurred while generating the summary.")

        @self.telethon_client.on(events.NewMessage)
        async def handle_new_message(event):
            """Handle new messages."""
            try:
                if not event.text or event.message.out:
                    return

                sender = await event.get_sender()
                chat = await event.get_chat()

                if sender is None:
                    print(f"⚠️ Message from unknown sender in chat {chat.title if chat else 'Unknown Chat'}")
                    sender_username = "Unknown User"
                else:
                    sender_username = f"@{sender.username}" if sender.username else sender.first_name

                message_data = {
                    "id": str(event.message.id),
                    "text": event.text,
                    "sender_username": sender_username,
                    "action": "mentioned" if event.message.mentioned else "replied" if event.message.reply_to else "wrote",
                    "chat_name": chat.title if hasattr(chat, "title") and chat.title else "Private Chat",
                    "chat_id": chat.id,
                    "timestamp": event.message.date.timestamp()
                }
                await self.message_processor.process_message.remote(message_data)
            except Exception as e:
                print(f"❌ Error handling new message: {e}")

        @self.dp.message(Command("add_account"))
        async def handle_add_account(message):
            """Handle the /add_account command."""
            try:
                accounts = message.text.split()[1:]
                if not accounts:
                    await message.answer("❌ Please specify accounts to add.")
                    return

                results = []
                for account in accounts:
                    account = account.strip("@")
                    success = await self.tweet_processor.add_account.remote(account)
                    results.append(f"{'✅' if success else '❌'} @{account}")
                await message.answer("\n".join(results))
            except Exception as e:
                print(f"❌ Error adding account: {e}")
                await message.answer("❌ Failed to add accounts. Please try again.")

        @self.telethon_client.on(events.NewMessage(pattern='/new_style'))
        async def handle_new_style_command(event):
            """Handle the /new_style command."""
            try:
                success = await self.avatar_agent.update_user_style.remote(
                    self.telethon_client, event.sender_id
                )
                if success:
                    await event.respond("✅ Communication style updated successfully!")
                else:
                    await event.respond("❌ Failed to update communication style.")
            except Exception as e:
                print(f"❌ Error handling new style command: {e}")
                await event.respond("❌ An error occurred while updating style.")

        @self.telethon_client.on(events.NewMessage)
        async def handle_avatar_message(event):
            """Handle messages for AI avatar."""
            if event.out or event.text.startswith('/'):
                return

            try:
                message_data = {
                    'user_id': event.sender_id,
                    'text': event.text
                }
                response = await self.avatar_agent.process_message.remote(message_data)
                await event.respond(response)
            except Exception as e:
                print(f"❌ Error handling avatar message: {e}")
                await event.respond("❌ An error occurred while processing your message.")

    async def process_tweets_periodically(self):
        """Process tweets at regular intervals."""
        while True:
            try:
                print("🔄 Checking for new tweets...")
                summary = await self.tweet_processor.process_new_tweets.remote()
                if summary:
                    print("✅ Tweet summary generated")
                    await self.aiogram_bot.send_message(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        text=summary,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    print("ℹ️ No new tweets to process")
            except Exception as e:
                print(f"❌ Error processing tweets: {e}")
            await asyncio.sleep(30)

    async def start(self):
        """Start the orchestrator."""
        print("🚀 Starting orchestrator...")
        await self.telethon_client.connect()
        if not await self.telethon_client.is_user_authorized():
            print("⏳ Authorization required")
            phone = input("Enter your phone number: ").strip()
            await self.telethon_client.send_code_request(phone)
            code = input("Enter SMS code: ").strip()
            try:
                await self.telethon_client.sign_in(phone=phone, code=code)
            except SessionPasswordNeededError:
                password = input("Enter your cloud password (2FA): ").strip()
                await self.telethon_client.sign_in(password=password)
        print("✅ Telethon client connected successfully!")
        await self.setup_handlers()
        await asyncio.gather(
            self.process_tweets_periodically(),
            self.dp.start_polling(self.aiogram_bot),
            self.telethon_client.run_until_disconnected()
        )


async def main():
    orchestrator = AgentOrchestrator()
    await orchestrator.start()


if __name__ == "__main__":
    asyncio.run(main())

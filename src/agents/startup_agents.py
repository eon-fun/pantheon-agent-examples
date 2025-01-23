import ray
import asyncio
from telethon import TelegramClient, events, functions
from telethon.errors import SessionPasswordNeededError
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from telethon.tl.types import InputPeerEmpty

from simple_ai_agents.ai_dialogue_manager.ray_dialogue_manager import MessageProcessor
from simple_ai_agents.ai_smm_manager.ray_news_agent import NewsAgent
from simple_ai_agents.ai_twitter_summary.ray_twitter_summary import TweetProcessor
from simple_ai_agents.ai_avatar.ray_avatar import AvatarAgent

# Configuration
API_ID = "26012476"
API_HASH = "d0ba6cd225c5dea4d2f7eb717adbeaac"
TELEGRAM_BOT_TOKEN = "8039253205:AAEFwlG0c2AmhwIXnqC9Q5TsBo_x-7jM2a0"
SESSION_NAME = "my_telegram_session"
TELEGRAM_CHANNEL_ID = "@panteoncryptonews"

NEWS_TELEGRAM_BOT_TOKEN = "7633131821:AAForOPCLS045IFHihMf49UozGwKL7IMbpU"
NEWS_TELEGRAM_CHANNEL_ID = "@pantheoncryptotest"


class AgentOrchestrator:
    def __init__(self):
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)
            print("✅ Ray initialized successfully!")

        # Initialize all agents
        self.news_agent = NewsAgent.remote()
        self.tweet_processor = TweetProcessor.remote()
        self.message_processor = MessageProcessor.remote()
        self.avatar_agent = AvatarAgent.remote()

        # Initialize bots and clients
        self.telethon_client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
        self.aiogram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.aiogram_bot_news = Bot(token=NEWS_TELEGRAM_BOT_TOKEN)
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

        # Регистрируем обработчики команд для aiogram
        self.dp.message.register(self.handle_add_account, Command("add_account"))
        self.dp.message.register(self.handle_add_news_site, Command("add_news_site"))

        # Обработчики для Telethon
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

    async def handle_add_account(self, message: types.Message):
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

            response = "\n".join(results)
            print(f"Adding accounts response: {response}")
            await message.answer(response)

        except Exception as e:
            error_msg = f"❌ Error adding account: {str(e)}"
            print(error_msg)
            await message.answer(error_msg)

    async def handle_add_news_site(self, message: types.Message):
        """Handle the /add_news_site command."""
        try:
            sites = message.text.split()[1:]
            if not sites:
                await message.answer("❌ Please specify news sites to add.")
                return

            results = []
            for site in sites:
                success = await self.news_agent.add_news_site.remote(site)
                results.append(f"{'✅' if success else '❌'} {site}")

            response = "\n".join(results)
            print(f"Adding news sites response: {response}")
            await message.answer(response)

        except Exception as e:
            error_msg = f"❌ Error adding news site: {str(e)}"
            print(error_msg)
            await message.answer(error_msg)

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

    async def process_news_periodically(self):
        """Process news at regular intervals."""
        try:
            while True:
                try:
                    print("🔄 Checking for new articles...")
                    summaries = await self.news_agent.process_new_content.remote()

                    if summaries:
                        print("✅ News summaries generated")
                        for summary in summaries:
                            try:
                                await self.aiogram_bot_news.send_message(
                                    chat_id=NEWS_TELEGRAM_CHANNEL_ID,
                                    text=summary,
                                    parse_mode=ParseMode.MARKDOWN
                                )
                                await asyncio.sleep(2)
                            except Exception as e:
                                print(f"❌ Error sending message to Telegram: {e}")
                    else:
                        print("ℹ️ No new articles to process")
                except Exception as e:
                    print(f"❌ Error processing news: {e}")

                await asyncio.sleep(30)
        except Exception as e:
            print(f"❌ Fatal error in news processing: {e}")

    async def start(self):
        """Start the orchestrator."""
        print("🚀 Starting orchestrator...")

        # Инициализация Telethon клиента
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

        # Настройка обработчиков
        await self.setup_handlers()

        # Запуск всех компонентов
        dp_task_1 = asyncio.create_task(self.dp.start_polling(self.aiogram_bot))
        dp_task_2 = asyncio.create_task(self.dp.start_polling(self.aiogram_bot_news))
        tweets_task = asyncio.create_task(self.process_tweets_periodically())
        news_task = asyncio.create_task(self.process_news_periodically())
        telethon_task = asyncio.create_task(self.telethon_client.run_until_disconnected())

        # Ждем завершения всех задач
        await asyncio.gather(
            dp_task_1,
            dp_task_2,
            tweets_task,
            news_task,
            telethon_task
        )


async def main():
    orchestrator = AgentOrchestrator()
    await orchestrator.start()


if __name__ == "__main__":
    asyncio.run(main())

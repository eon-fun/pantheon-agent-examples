import ray
import asyncio
from telethon import TelegramClient, events, functions
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import InputPeerEmpty, PeerUser, PeerChannel, PeerChat
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.enums import ParseMode
import aiohttp
import json
from html import escape
from database.redis.redis_client import RedisDB
from services.ai_tools.openai_client import send_openai_request

# Configuration
TELEGRAM_BOT_TOKEN = "8039253205:AAEFwlG0c2AmhwIXnqC9Q5TsBo_x-7jM2a0"
TELEGRAM_CHANNEL_ID = "@panteoncryptonews"
API_ID = "26012476"
API_HASH = "d0ba6cd225c5dea4d2f7eb717adbeaac"
SESSION_NAME = "my_telegram_session"
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAALFxQEAAAAAccmjfpy9O9AoKsiWm3EiKRmlYW0%3DKxQgwMPoButLHfAL1Zoledy4bdko6ufQNLTQuxDpCfZxfgthkI'

# Redis Keys
REDIS_MESSAGES_KEY = "telegram_messages"
REDIS_LAST_PROCESSED_TWEETS = "last_processed_tweets"
REDIS_SUBSCRIBED_TWITTER_ACCOUNTS = "subscribed_twitter_accounts"

# AI Prompts
TELEGRAM_PROMPT = """
You are an assistant summarizing messages in a chat. 
Your task is to create a brief summary of what each user discussed without answering any questions. 
For example: 
@username mentioned something about topic X.
@another_user brought up another topic Y.
Also note if someone was mentioned or replied to in the chat and include the chat name. 
Do not provide solutions, just summarize the content of the messages concisely.
"""

TWITTER_PROMPT = """
You are a social media analyst and news summarizer for a cryptocurrency and celebrity news channel. Your task is to monitor tweets and create concise summaries that highlight key events, their potential consequences, and the involved parties. 

When summarizing tweets:
- Combine related tweets into one coherent summary.
- Clearly state the main events or announcements, e.g., "Famous investor John Doe announces plans to buy BTC."
- Explain possible implications or market reactions, e.g., "This could lead to increased confidence in BTC."
- Include usernames of involved people or accounts when relevant, e.g., "@johndoe."
- If the tweets reflect a conflict or interaction, summarize the core of the conflict, e.g., "A heated exchange between @star1 and @star2 about recent controversies."
- Use engaging and clear language suitable for Telegram posts in English. Use HTML formatting for beautify text.

End the summary with an engaging closing line like "Stay tuned for updates! 🚀" or similar.
"""


@ray.remote
class MessageProcessor:
    def __init__(self):
        self.db = RedisDB()

    async def process_message(self, message_data):
        try:
            self.db.add_to_sorted_set(
                REDIS_MESSAGES_KEY,
                int(message_data["timestamp"]),
                json.dumps(message_data)
            )
            print(f"✅ Message saved from chat '{message_data['chat_name']}': {message_data['text'][:50]}...")
        except Exception as e:
            print(f"❌ Error processing message: {e}")

    async def update_read_messages(self, read_messages_data):
        try:
            messages = self.db.get_sorted_set(REDIS_MESSAGES_KEY)
            if not messages:
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
        try:
            messages = self.db.get_sorted_set(REDIS_MESSAGES_KEY)
            if not messages:
                return "No messages to process."

            combined_text = "\n".join([
                f"[{json.loads(msg)['chat_name']}] {json.loads(msg)['sender_username']} {json.loads(msg)['action']}: {json.loads(msg)['text']}"
                for msg in messages
            ])

            self.db.delete(REDIS_MESSAGES_KEY)

            messages = [
                {"role": "system", "content": TELEGRAM_PROMPT},
                {"role": "user", "content": combined_text}
            ]

            summary = await send_openai_request(messages)
            return summary.strip()

        except Exception as e:
            print(f"Detailed summary error: {str(e)}")
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


@ray.remote
class TweetProcessor:
    def __init__(self):
        self.db = RedisDB()
        self.headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

    def _decode_redis_set(self, redis_set):
        """Helper function to properly decode Redis set items"""
        result = set()
        for item in redis_set:
            if isinstance(item, bytes):
                result.add(item.decode('utf-8'))
            else:
                result.add(str(item))
        return result

    async def add_account(self, account):
        try:
            self.db.r.sadd(REDIS_SUBSCRIBED_TWITTER_ACCOUNTS, account)
            print(f"✅ Account added: {account}")
            return True
        except Exception as e:
            print(f"❌ Error adding account {account}: {e}")
            return False

    async def fetch_tweets(self, account):
        try:
            processed_ids = self._decode_redis_set(
                self.db.get_set(REDIS_LAST_PROCESSED_TWEETS)
            )

            user_url = f"https://api.twitter.com/2/users/by/username/{account}"
            async with aiohttp.ClientSession() as session:
                user_resp = await session.get(user_url, headers=self.headers)
                user_data = await user_resp.json()

                if "data" not in user_data:
                    return []

                user_id = user_data["data"]["id"]
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                tweets_resp = await session.get(tweets_url, headers=self.headers)
                tweets_data = await tweets_resp.json()

                if "data" not in tweets_data:
                    return []

                new_tweets = []
                for tweet in tweets_data["data"]:
                    if tweet["id"] not in processed_ids:
                        tweet_data = {
                            "id": tweet["id"],
                            "account": account,
                            "text": tweet["text"]
                        }
                        new_tweets.append(tweet_data)

                return new_tweets
        except Exception as e:
            print(f"❌ Error fetching tweets for @{account}: {e}")
            return []

    async def process_new_tweets(self):
        try:
            accounts = self._decode_redis_set(
                self.db.get_set(REDIS_SUBSCRIBED_TWITTER_ACCOUNTS)
            )

            if not accounts:
                return None

            all_tweets = []
            for account in accounts:
                tweets = await self.fetch_tweets(account)
                all_tweets.extend(tweets)

            if all_tweets:
                tweet_texts = [f"@{tweet['account']}: {tweet['text']}" for tweet in all_tweets]
                combined_text = "\n\n".join(tweet_texts)

                messages = [
                    {"role": "system", "content": TWITTER_PROMPT},
                    {"role": "user", "content": f"Here are the tweets:\n\n{combined_text}"}
                ]

                summary = await send_openai_request(messages)
                for tweet in all_tweets:
                    self.db.r.sadd(REDIS_LAST_PROCESSED_TWEETS, tweet['id'])
                return escape(summary.strip())

            return None

        except Exception as e:
            print(f"❌ Error in process_new_tweets: {e}")
            return None


class AgentOrchestrator:
    def __init__(self):
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)
            print("Ray initialized successfully!")

        self.message_processor = MessageProcessor.remote()
        self.tweet_processor = TweetProcessor.remote()
        self.telethon_client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
        self.aiogram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()

    async def setup_handlers(self):
        @self.telethon_client.on(events.NewMessage(pattern="/summary"))
        async def handle_summary_command(event):
            try:
                await event.respond("⏳ Generating summary, please wait...")
                read_messages_data = await get_read_messages_data(self.telethon_client)
                await self.message_processor.update_read_messages.remote(read_messages_data)
                summary = await self.message_processor.generate_summary.remote()
                await event.respond(f"📋 Summary:\n{summary}")
            except Exception as e:
                error_msg = f"❌ Error generating summary: {str(e)}"
                print(error_msg)
                await event.respond(error_msg)

        @self.telethon_client.on(events.NewMessage)
        async def handle_new_message(event):
            try:
                if not event.text or event.message.out:
                    return

                sender = await event.get_sender()
                chat = await event.get_chat()

                if sender is None:
                    sender_username = "Unknown User"
                else:
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

                await self.message_processor.process_message.remote(message_data)
            except Exception as e:
                print(f"❌ Error handling message: {e}")

        @self.dp.message(Command("add_account"))
        async def handle_add_account(message):
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
                print(f"❌ Error in /add_account: {e}")
                await message.answer("❌ Failed to add accounts. Please try again.")

    async def process_tweets_periodically(self):
        while True:
            try:
                print("🔄 Checking for new tweets...")
                summary = await self.tweet_processor.process_new_tweets.remote()

                if summary:
                    await self.aiogram_bot.send_message(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        text=summary,
                        parse_mode=ParseMode.HTML
                    )
                    print("✅ Tweet summary sent successfully")
                else:
                    print("ℹ️ No new tweets to process")
            except Exception as e:
                print(f"❌ Error in tweet processing: {e}")

            await asyncio.sleep(30)

    async def start(self):
        try:
            print("🚀 Starting Telethon client")
            await self.telethon_client.connect()

            if not await self.telethon_client.is_user_authorized():
                print("⏳ Authentication required")
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

        except Exception as e:
            print(f"❌ Startup error: {e}")
        finally:
            await self.telethon_client.disconnect()
            await self.aiogram_bot.session.close()


async def main():
    orchestrator = AgentOrchestrator()
    await orchestrator.start()


if __name__ == "__main__":
    asyncio.run(main())

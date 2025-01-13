import asyncio
import aiohttp
from html import escape
from aiogram.enums import ParseMode
from aiohttp import ClientTimeout
from tenacity import retry, stop_after_attempt, wait_fixed
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from database.redis.redis_client import RedisDB
from services.ai_tools.openai_client import send_openai_request

# Константы и конфигурация
TELEGRAM_BOT_TOKEN = "8039253205:AAEFwlG0c2AmhwIXnqC9Q5TsBo_x-7jM2a0"
TELEGRAM_CHANNEL_ID = "@panteoncryptonews"
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAALFxQEAAAAAccmjfpy9O9AoKsiWm3EiKRmlYW0%3DKxQgwMPoButLHfAL1Zoledy4bdko6ufQNLTQuxDpCfZxfgthkI'

REDIS_LAST_PROCESSED_TWEETS = "last_processed_tweets"
REDIS_SUBSCRIBED_TWITTER_ACCOUNTS = "subscribed_twitter_accounts"
REDIS_TWEETS_TO_PROCESS = "tweets_to_process"

AI_PROMPT = """
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

# Инициализация Redis и Telegram
db = RedisDB()
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
timeout = ClientTimeout(total=10)


# Функция для экранирования HTML
def escape_html(text: str) -> str:
    """
    Экранирует специальные символы для HTML и заменяет переносы строк.
    """
    return escape(text).replace('\n', '\n')


# Функция для добавления сообщения в очередь
async def add_to_queue(text: str):
    print(f"📝 Добавление в очередь: {text[:50]}...")
    await message_queue.put(text)


# --- Функция для добавления аккаунтов ---
@dp.message(Command("add_account"))
async def add_account(message: Message):
    accounts = message.text.split()[1:]
    if not accounts:
        await message.reply("❌ Пожалуйста, укажите аккаунты для добавления.")
        return
    for account in accounts:
        db.add_to_set(REDIS_SUBSCRIBED_TWITTER_ACCOUNTS, account.strip("@"))
    await message.reply(f"✅ Аккаунты добавлены: {', '.join(accounts)}")


# --- Функция для удаления аккаунтов ---
@dp.message(Command("remove_account"))
async def remove_account(message: Message):
    accounts = message.text.split()[1:]
    if not accounts:
        await message.reply("❌ Пожалуйста, укажите аккаунты для удаления.")
        return
    for account in accounts:
        db.r.srem(REDIS_SUBSCRIBED_TWITTER_ACCOUNTS, account.strip("@"))
    await message.reply(f"✅ Аккаунты удалены: {', '.join(accounts)}")


# Функция получения твитов с повторными попытками
@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), reraise=True)
async def fetch_with_retry(url, headers, session):
    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            raise aiohttp.ClientResponseError(
                request_info=resp.request_info,
                history=resp.history,
                status=resp.status,
                message=f"Ошибка {resp.status} при запросе к {url}",
                headers=resp.headers
            )
        return await resp.json()


# --- Функция для получения твитов ---
async def fetch_tweets():
    accounts = db.get_set(REDIS_SUBSCRIBED_TWITTER_ACCOUNTS)
    processed_tweets = db.get_set(REDIS_LAST_PROCESSED_TWEETS)
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    new_tweets = []

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for account in accounts:
            try:
                print(f"🔍 Получение твитов для @{account}")
                user_url = f"https://api.twitter.com/2/users/by/username/{account}"
                user_data = await fetch_with_retry(user_url, headers, session)
                if "data" not in user_data:
                    print(f"⚠️ Не удалось получить user_id для @{account}")
                    continue

                user_id = user_data["data"]["id"]

                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                tweets_data = await fetch_with_retry(tweets_url, headers, session)
                if "data" not in tweets_data or not tweets_data["data"]:
                    print(f"⚠️ Нет доступных твитов для @{account}")
                    continue

                for tweet in tweets_data["data"]:
                    if tweet["id"] not in processed_tweets:
                        db.add_to_set(REDIS_LAST_PROCESSED_TWEETS, tweet["id"])
                        db.add_to_set(REDIS_TWEETS_TO_PROCESS, f"@{account}: {tweet['text']}")
                        print(f"✅ Новый твит: {tweet['text'][:50]}...")

            except aiohttp.ClientResponseError as e:
                print(f"❌ Ошибка {e.status} для @{account}: {e.message}")
            except asyncio.TimeoutError:
                print(f"⚠️ Таймаут при запросе для @{account}. Пропускаем.")
            except Exception as e:
                print(f"❌ Неизвестная ошибка для @{account}: {e}")


# --- Функция для создания сводки ---
async def summarize_tweets(tweets):
    combined_text = "\n\n".join(tweets)
    messages = [
        {"role": "system", "content": AI_PROMPT},
        {"role": "user", "content": f"Here are the tweets:\n\n{combined_text}"}
    ]
    try:
        summary = await send_openai_request(messages)
        return escape_html(summary.strip())
    except Exception as e:
        print(f"❌ Ошибка создания сводки: {e}")
        return None


# --- Основная функция обработки и публикации твитов ---
async def process_and_publish_tweets():
    tweets = db.get_set(REDIS_TWEETS_TO_PROCESS)
    if tweets:
        tweets = [tweet.decode('utf-8') if isinstance(tweet, bytes) else tweet for tweet in tweets]
        db.r.delete(REDIS_TWEETS_TO_PROCESS)  # Удаляем после обработки
        summary = await summarize_tweets(tweets)
        if summary:
            try:
                print(f"📤 Отправка сообщения: {summary[:50]}...")
                await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=summary, parse_mode=ParseMode.HTML)
            except Exception as e:
                print(f"❌ Ошибка отправки сообщения: {e}")
        else:
            print("⚠️ Сводка не создана.")
    else:
        print("⚠️ Нет новых твитов для обработки.")


# --- Периодическая задача ---
async def periodic_task():
    while True:
        print("🔄 Проверка новых твитов...")
        await fetch_tweets()
        await process_and_publish_tweets()
        await asyncio.sleep(30)


# --- Основная функция ---
async def main():
    asyncio.create_task(periodic_task())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
from urllib.parse import urljoin

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import ClientConnectorError
from bs4 import BeautifulSoup
from database.redis.redis_client import RedisDB
from services.ai_connectors.openai_client import send_openai_request
from tenacity import retry, stop_after_attempt, wait_fixed

# Инициализация Redis
db = RedisDB()
PROCESSED_LINKS_KEY = "processed_articles"
NEWS_SITES_KEY = "news_sites"
TWITTER_ACCOUNTS_KEY = "twitter_accounts"
PROCESSED_TWEETS_KEY = "processed_tweets"

# Telegram конфигурация
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@your_channel")

TWITTER_BASIC_BEARER_TOKEN = os.getenv("TWITTER_BASIC_BEARER_TOKEN")
GROK_API_URL = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
GROK_API_KEY = os.getenv("GROK_API_KEY")

PROMPT = (
    "You are a Telegram post author for a cryptocurrency news channel. "
    "Write concise and engaging posts in English with proper Markdown formatting. "
    "But dont use ###."
)
"Extract the most important points from the input text, include a short "
"headline with emojis, highlight key terms or names using bold formatting, "
"and use italic for emphasis. End the post with a simple, engaging closing "
"line like 'Stay tuned for more updates! 🚀📈' or similar. And some hashtags."

GROK_PROMPT = "You need to search for the hottest tweets and news for a given query"

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Очередь сообщений
message_queue = asyncio.Queue()


# 1. Добавление сообщений в очередь
async def add_to_queue(text: str):
    await message_queue.put(text)
    print(f"📝 Сообщение добавлено в очередь: {text[:50]}...")


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
async def send_message_with_retry(chat_id, text):
    """Функция для отправки сообщения с повторными попытками."""
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except ClientConnectorError as e:
        print(f"❌ Ошибка соединения с Telegram API: {e}")
        raise  # Повторяем попытку


# 2. Обработчик очереди сообщений
async def message_sender():
    print("🚀 Запущен обработчик очереди сообщений.")
    while True:
        message = await message_queue.get()
        try:
            print(f"📤 Отправка сообщения: {message[:50]}...")
            await send_message_with_retry(chat_id=TELEGRAM_CHANNEL_ID, text=message)
            await asyncio.sleep(30)  # Пауза в очереди между отправкой постов в телеграмм
        except Exception as e:
            print(f"❌ Ошибка при отправке сообщения: {e}")
        finally:
            message_queue.task_done()


# 3. Интеграция с Grok AI для поиска твитов
async def fetch_tweets_from_grok(query: str):
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "grok-beta",
        "messages": [{"role": "system", "content": GROK_PROMPT}, {"role": "user", "content": query}],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROK_API_URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    print(f"\u274c Ошибка при запросе к Grok: Статус {response.status}")
                    response_text = await response.text()
                    print(f"Ответ сервера: {response_text}")
                    return []

                data = await response.json()
                print(f"\u2705 Ответ от Grok: {data}")

                # Извлекаем содержимое твитов
                choices = data.get("choices", [])
                tweets = []
                for choice in choices:
                    message = choice.get("message", {})
                    content = message.get("content")
                    if content:
                        tweets.append(content)

                return tweets

    except Exception as e:
        print(f"\u274c Ошибка при обращении к Grok: {e}")
        return []


# 4. Обработка текста через GPT
async def rewrite_text(text):
    messages = [{"role": "system", "content": PROMPT}, {"role": "user", "content": text}]
    try:
        ai_response = await send_openai_request(messages)
        return ai_response.strip()
    except Exception as e:
        return f"Ошибка обработки текста: {e}"


@dp.message(Command("find_in_grok"))
async def find_in_grok(message: Message):
    query = message.text[len("/find_in_grok ") :].strip()
    if not query:
        await message.reply("⚠️ Укажите запрос для поиска в Grok.")
        return

    print(f"🔍 Поиск твитов в Grok по запросу: {query}")
    tweets = await fetch_tweets_from_grok(query)

    if not tweets:
        await message.reply("❌ Не удалось найти твиты по вашему запросу.")
        return

    for tweet in tweets:
        rewritten = await rewrite_text(tweet)
        await add_to_queue(rewritten)
    await message.reply("✅ Твиты добавлены в очередь для публикации.")


# 3. Сбор ссылок с сайтов
async def fetch_latest_articles(base_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    keywords = ["news", "article", "post", "blog", "story"]

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.get(base_url, headers=headers) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                article_links = {
                    urljoin(base_url, link["href"])
                    for link in soup.find_all("a", href=True)
                    if any(keyword in link["href"].lower() for keyword in keywords)
                }
                print(f"🔗 Найдено {len(article_links)} статей на {base_url}")
                return article_links
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Ошибка соединения с {base_url}: {e}")
    except asyncio.TimeoutError:
        print(f"❌ Таймаут при попытке подключения к {base_url}")
    except Exception as e:
        print(f"❌ Другая ошибка при получении статей с {base_url}: {e}")
    return set()


async def scrape_site(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), "html.parser")
                paragraphs = soup.find_all("p")
                return " ".join([p.get_text() for p in paragraphs])
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Ошибка соединения при парсинге {url}: {e}")
    except asyncio.TimeoutError:
        print(f"❌ Таймаут при парсинге {url}")
    except Exception as e:
        print(f"❌ Другая ошибка парсинга {url}: {e}")
    return None


# 5. Получение твитов с аккаунтов
async def fetch_tweets_from_accounts():
    accounts = db.get_set(TWITTER_ACCOUNTS_KEY)
    processed_tweets = set(db.get_set(PROCESSED_TWEETS_KEY))
    all_tweets = []

    BEARER_TOKEN = TWITTER_BASIC_BEARER_TOKEN
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    for account in accounts:
        try:
            print(f"🔍 Получение твитов для @{account}")
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(ssl=False),  # Отключаем SSL-верификацию
            ) as session:
                # Шаг 1: Получаем user_id по username
                user_info_url = f"https://api.twitter.com/2/users/by/username/{account}"
                async with session.get(user_info_url, headers=headers) as resp:
                    if resp.status != 200:
                        print(f"❌ Не удалось получить user_id для @{account}. Статус: {resp.status}")
                        continue

                    user_data = await resp.json()
                    if "data" not in user_data:
                        print(f"❌ Аккаунт @{account} не найден.")
                        continue

                    user_id = user_data["data"]["id"]

                # Шаг 2: Получаем твиты пользователя
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                params = {"max_results": 5}  # Максимальное количество твитов
                async with session.get(tweets_url, headers=headers, params=params) as resp:
                    if resp.status != 200:
                        print(f"❌ Не удалось получить твиты для @{account}. Статус: {resp.status}")
                        continue

                    tweets_data = await resp.json()
                    if "data" not in tweets_data:
                        print(f"❌ Твиты для @{account} не найдены.")
                        continue

                    # Обрабатываем новые твиты
                    for tweet in tweets_data.get("data", []):
                        if tweet["id"] not in processed_tweets:
                            db.add_to_set(PROCESSED_TWEETS_KEY, tweet["id"])
                            all_tweets.append(tweet["text"])
                            print(f"✅ Новый твит: {tweet['text'][:50]}...")

        except aiohttp.ClientConnectorError as e:
            print(f"❌ Ошибка соединения с Twitter для @{account}: {e}")
        except asyncio.TimeoutError:
            print(f"❌ Таймаут при получении твитов для @{account}")
        except Exception as e:
            print(f"❌ Другая ошибка при получении твитов для @{account}: {e}")

    return all_tweets


# 7. Основная обработка статей и твитов
async def process_new_articles():
    news_sites = db.get_set(NEWS_SITES_KEY)
    processed_links = set(db.get_set(PROCESSED_LINKS_KEY))

    for site in news_sites:
        new_links = await fetch_latest_articles(site)
        for link in new_links - processed_links:
            text = await scrape_site(link)
            if text:
                rewritten = await rewrite_text(text)
                await add_to_queue(rewritten)
                db.add_to_set(PROCESSED_LINKS_KEY, link)


async def process_twitter_posts():
    tweets = await fetch_tweets_from_accounts()
    for tweet in tweets:
        rewritten = await rewrite_text(tweet)
        await add_to_queue(rewritten)


# 8. Команды бота
@dp.message(Command("add_links"))
async def add_links(message: Message):
    links = message.text.split()[1:]
    for link in links:
        db.add_to_set(NEWS_SITES_KEY, link)
    await message.reply("✅ Сайты добавлены!")


@dp.message(Command("add_x_account"))
async def add_twitter_account(message: Message):
    accounts = message.text.split()[1:]
    for account in accounts:
        db.add_to_set(TWITTER_ACCOUNTS_KEY, account.strip("@"))
    await message.reply("✅ Twitter аккаунты добавлены!")


# 9. Периодическая задача
async def periodic_task():
    while True:
        print("🔎 Проверка статей и твитов...")
        await process_new_articles()
        await process_twitter_posts()
        await asyncio.sleep(
            10
        )  # Пауза в поиске статьей и твитов. Рекомендую минимум 1 час, пока в тест режиме - 10 сек


# 10. Главная функция
async def main():
    asyncio.create_task(message_sender())  # Запускаем обработчик очереди
    asyncio.create_task(periodic_task())  # Периодическая проверка
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

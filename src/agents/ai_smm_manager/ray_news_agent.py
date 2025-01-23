import ray
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from aiohttp import ClientConnectorError
from tenacity import retry, stop_after_attempt, wait_fixed
from aiogram.enums import ParseMode

from database.redis.redis_client import RedisDB
from services.ai_tools.openai_client import send_openai_request

PROMPT = """
You are a Telegram post author for a cryptocurrency news channel. 
Write concise and engaging posts in English with proper Markdown formatting. 
But dont use ###.
Extract the most important points from the input text, include a short 
headline with emojis, highlight key terms or names using bold formatting, 
and use italic for emphasis. End the post with a simple, engaging closing 
line like 'Stay tuned for more updates! 🚀📈' or similar. And some hashtags.
"""


@ray.remote
class NewsAgent:
    def __init__(self):
        self.db = RedisDB()
        self.processed_links_key = "processed_articles"
        self.news_sites_key = "news_sites"
        print("✅ NewsAgent initialized")

    async def add_news_site(self, site):
        """Adds a news site to monitor."""
        try:
            self.db.add_to_set(self.news_sites_key, site)
            print(f"✅ News site added: {site}")
            return True
        except Exception as e:
            print(f"❌ Error adding news site {site}: {e}")
            return False

    async def fetch_latest_articles(self, base_url):
        """Fetches latest article links from a news site."""
        headers = {"User-Agent": "Mozilla/5.0"}
        keywords = ["news", "article", "post", "blog", "story", "business", "sponsored-content", "markets"]

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
                    print(f"🔗 Found {len(article_links)} articles on {base_url}")
                    return article_links
        except Exception as e:
            print(f"❌ Error fetching articles from {base_url}: {e}")
            return set()

    async def scrape_article(self, url):
        """Scrapes content from an article."""
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    paragraphs = soup.find_all('p')
                    return ' '.join([p.get_text() for p in paragraphs])
        except Exception as e:
            print(f"❌ Error scraping article {url}: {e}")
            return None

    async def process_article(self, text):
        """Processes article text through AI."""
        messages = [{"role": "system", "content": PROMPT}, {"role": "user", "content": text}]
        try:
            response = await send_openai_request(messages)
            return response.strip()
        except Exception as e:
            print(f"❌ Error processing article text: {e}")
            return None

    async def process_new_content(self):
        """Main method to process new articles and generate summaries."""
        try:
            news_sites = self.db.get_set(self.news_sites_key)
            processed_links = set(self.db.get_set(self.processed_links_key))

            summaries = []
            for site in news_sites:
                new_links = await self.fetch_latest_articles(site)
                for link in new_links - processed_links:
                    print("Article to summarize - ", link)
                    text = await self.scrape_article(link)
                    if text:
                        summary = await self.process_article(text)
                        if summary:
                            summaries.append(summary)
                            self.db.add_to_set(self.processed_links_key, link)

            return summaries if summaries else None
        except Exception as e:
            print(f"❌ Error in process_new_content: {e}")
            return None

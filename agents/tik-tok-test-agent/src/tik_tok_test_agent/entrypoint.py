import os
import subprocess
from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from ray import serve
from tik_tok_package.main import TikTokBot


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


def install_chrome_linux():
    subprocess.run(["sudo", "apt", "update"], check=False)
    subprocess.run(["sudo", "apt", "install", "-y", "google-chrome-stable"], check=False)
    link = subprocess.run(
        ["readlink", "-f", "$(which google-chrome)"], capture_output=True, shell=True, text=True, check=False
    )
    return link


@serve.deployment
@serve.ingress(app)
class TwitterAmbassadorCommentsAnswerer(BaseAgent):
    def __init__(self):
        self.running_tasks = {}

    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        return await self.answer_on_project_tweets_comments(goal)

    async def answer_on_project_tweets_comments(
        self,
        goal: str,
    ):
        try:
            print("Starting TikTok bot...")
            username = os.getenv("TIKTOK_USERNAME")
            password = os.getenv("TIKTOK_PASSWORD")
            api_key = os.getenv("TIKTOK_API_KEY")
            print("Installing Chrome...")
            bot = TikTokBot(api_key=api_key, headless=False)
            print("Chrome installed")
            bot.login(username, password)
            print("Login successful")
            bot.comment_on_video(
                video_url="https://www.tiktok.com/@mini_lolik/video/7491613049669897527",
                comment="Hello world!_test_test",
            )
            print("Comment posted successfully")
            try:
                print("Quitting bot...")
                bot.quit()
            except Exception:
                pass

            return {"success": True}
        except Exception as e:
            print(f"Error occurred: {e}")
            try:
                bot.quit()
            except Exception:
                pass
            return {"success": False, "error": str(e)}


def get_agent(agent_args: dict):
    return TwitterAmbassadorCommentsAnswerer.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")

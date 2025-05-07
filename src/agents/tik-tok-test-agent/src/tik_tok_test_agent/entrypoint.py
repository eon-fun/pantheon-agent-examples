from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent.ray_entrypoint import BaseAgent
from tik_tok_package.main import TikTokBot
import subprocess

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

def install_chrome_linux():
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "-y", "google-chrome-stable"])
    link = subprocess.run(["readlink", "-f", "$(which google-chrome)"], capture_output=True, shell=True, text=True)
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
            link=install_chrome_linux()

            username = "valebtinbest@gmail.com"
            password = "|yR2mZtbc;hjS/T"
            api_key = "5baa59265de642a543eeb985ec276708"
            bot = TikTokBot(api_key=api_key, headless=False,browser_executable_path=link)
            bot.login(username, password)
            bot.comment_on_video(
                video_url="https://www.tiktok.com/@mini_lolik/video/7491613049669897527",
                comment="Hello world!_test_test"
            )
            try:
                bot.quit()
            except Exception:
                pass

            return {"success": True}
        except Exception as e:
            print(f"Error occurred: {e}")
            return {"success": False, "error": str(e)}


def get_agent(agent_args: dict):
    return TwitterAmbassadorCommentsAnswerer.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
from contextlib import asynccontextmanager
from fastapi import FastAPI
from ray import serve
from base_agent.ray_entrypoint import BaseAgent
from tik_tok_package.main import TikTokBot


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@serve.deployment
@serve.ingress(app)
class TwitterAmbassadorCommentsAnswerer(BaseAgent):
    def __init__(self):
        self.running_tasks = {}

    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None):
        await self.answer_on_project_tweets_comments(goal)

    async def answer_on_project_tweets_comments(
            self,
            goal: str,
    ) -> bool:
        username = "valebtinbest@gmail.com"
        password = "|yR2mZtbc;hjS/T"
        api_key = "5baa59265de642a543eeb985ec276708"
        bot = TikTokBot(api_key=api_key, headless=False)
        bot.login(username, password)
        bot.comment_on_video(
            video_url="https://www.tiktok.com/@mini_lolik/video/7491613049669897527",
            comment="Hello world!_test_test"
        )
        try:
            bot.quit()
        except Exception:
            pass


def get_agent(agent_args: dict):
    return TwitterAmbassadorCommentsAnswerer.bind(**agent_args)


if __name__ == "__main__":
    serve.run(app, route_prefix="/")
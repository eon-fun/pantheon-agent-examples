from contextlib import asynccontextmanager

from base_agent.ray_entrypoint import BaseAgent
from base_agent.prompt.utils import get_environment
from fastapi import FastAPI
from ray import serve
from pydantic import BaseModel
# from tenacity import retry, stop_after_attempt, wait_fixed

from qdrant_client_custom.main import get_qdrant_client
from redis_client.main import get_redis_db
from send_openai_request.main import get_embedding, send_openai_request


class InputModel(BaseModel):
    prompt: str


class OutputModel(BaseModel):
    success: bool
    result: str
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    # launch some tasks on app start
    yield
    # handle clean up

app = FastAPI(lifespan=lifespan)


# @serve.deployment
# class SubAgent:
#     """This agent is a part of ray serve application, but it is not exposed for communication with the outside agents.
#     We can use it to execute some tools or a custom logic to enable ray scaling capabilities.
#     The `__call__` method in this class suggests that it could also just be a function instead.
#     """

#     def __call__(self, *args, **kwds):
#         pass

# @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_openai_embedding(prompt: str):
    return await get_embedding(prompt)


@serve.deployment
@serve.ingress(app)
class PersonaAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.jinja_env = get_environment("persona_agent")

    @app.post("/{goal}")
    async def handle(self, goal: str, plan: dict | None = None, input_prompt: str | None = None):
        return await self.get_persona_template(goal, input_prompt)

    async def get_persona_template(self, goal: str, prompt: str):
        redis_db = get_redis_db()
        qdrant_client = get_qdrant_client()
        persona_collection = goal

        # заменить на проверку not exists в redis
        if not persona_collection:
            return "No persona collection found"

        desc_key = f"{goal}:description"
        persona_description = redis_db.get(desc_key) or ""

        embedding_input = await get_openai_embedding(prompt)

        search_similar_tweets = qdrant_client.search(
            collection_name=persona_collection,
            query_vector=embedding_input,
            limit=5
        )
        similar_tweets = [tweet.payload["text"] for tweet in search_similar_tweets]
        context = "\n".join(similar_tweets)

        # Используем Jinja2 для рендеринга шаблонов
        template = self.jinja_env.get_template(
            "prompts/generation_prompt.txt.j2")
        generation_prompt = template.render(
            persona_description=persona_description,
            context=context,
            prompt=prompt
        )

        # Также используем Jinja2 для системного сообщения
        system_template = self.jinja_env.get_template(
            "prompts/system_message.txt.j2")
        system_message = system_template.render()

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": generation_prompt}
        ]
        result = await send_openai_request(messages=messages, temperature=0.7)

        return OutputModel(success=True, result=result).model_dump()


# serve run entrypoint:app
app = PersonaAgent.bind()


if __name__ == "__main__":
    serve.run(app, route_prefix="/")

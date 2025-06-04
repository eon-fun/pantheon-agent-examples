from contextlib import asynccontextmanager

from base_agent.prompt.utils import get_environment
from base_agent.ray_entrypoint import BaseAgent
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client_custom.main import get_qdrant_client
from ray import serve
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


@serve.deployment
@serve.ingress(app)
class PersonaAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.jinja_env = get_environment("persona_agent")

    @app.post("/{goal}")
    async def handle(self, goal: str, input_prompt: str, plan: dict | None = None):
        """Generates a tweet in the style of the specified persona based on the prompt.

        Args:
            goal: persona collection name
            prompt: instruction for generation

        Returns:
            success: bool
            result: Generated tweet text in the persona's style

        """
        return await self.get_persona_template(goal, input_prompt)

    async def get_persona_template(self, goal: str, prompt: str):
        """Get the persona template"""
        redis_db = get_redis_db()
        qdrant_client = get_qdrant_client()
        persona_collection = goal

        # Check if the collection exists in Redis
        if not redis_db.r.exists(f"{persona_collection}:description"):
            return OutputModel(success=False, result="No persona collection found")

        desc_key = f"{goal}:description"
        persona_description = redis_db.get(desc_key) or ""

        embedding_input = await get_embedding(prompt)

        search_similar_tweets = qdrant_client.search(
            collection_name=persona_collection, query_vector=embedding_input, limit=5
        )
        similar_tweets = [tweet.payload["text"] for tweet in search_similar_tweets]
        context = "\n".join(similar_tweets)

        # Use Jinja2 for template rendering
        template = self.jinja_env.get_template("prompts/generation_prompt.txt.j2")
        generation_prompt = template.render(persona_description=persona_description, context=context, prompt=prompt)

        # Also use Jinja2 for system message
        system_template = self.jinja_env.get_template("prompts/system_message.txt.j2")
        system_message = system_template.render()

        messages = [{"role": "system", "content": system_message}, {"role": "user", "content": generation_prompt}]
        result = await send_openai_request(messages=messages, temperature=0.7)

        return OutputModel(success=True, result=result).model_dump()


# serve run entrypoint:app
app = PersonaAgent.bind()


if __name__ == "__main__":
    serve.run(app, route_prefix="/")

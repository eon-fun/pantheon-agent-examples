import random
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from kol_agent.config import get_config

config = get_config()

# LLM
model = ChatOpenAI(model="gpt-4.1-mini", temperature=0) 

class TweetContent(BaseModel):
    content: str

# Templates for different bot roles
ROLE_TEMPLATES = {
    "advocate": '''Write comment supporting the following post. Express agreement and add your own positive thoughts. Post content: "{context}"''',
    "skeptic": '''Write comment expressing skepticism or a critical viewpoint about the following post. Be polite and constructive. Post content: "{context}"''',
    "expert": '''Write comment on the following post from an expert's perspective. Mention relevant facts, research, or professional experience. Post content: "{context}"''',
    "moderator": '''Write comment as a moderator, summarizing the discussion and encouraging constructive conversation about the following post. Post content: "{context}"''',
    "enthusiast": '''Write enthusiastic and positive comment about the following post. Show excitement and interest. Post content: "{context}"''',
    "newbie": '''Write comment as a newcomer who is curious and wants to learn more about the following post. Ask a simple question or request clarification. Post content: "{context}"''',
}


def generate_content_by_role(role: str, context: str = None) -> str:
    """
    Generates content according to the bot's role

    Args:
        role (str): Bot role
        context (str, optional): Discussion context

    Returns:
        str: Generated content
    """
    template = ROLE_TEMPLATES.get(role, ROLE_TEMPLATES["advocate"])
    # Fill the template
    prompt = template.format(context=context)

    # Add details depending on the role
    response = model.with_structured_output(TweetContent).invoke(prompt)

    return response.content


from kol_agent.config import get_config
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

config = get_config()

# LLM
model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)


class TweetContent(BaseModel):
    content: str


# Templates for different bot roles
ROLE_TEMPLATES = {
    "advocate": '''Write a short, tweet-like supportive comment for the following post. Clearly express agreement, add your own positive thought, and include at least one emoji to convey encouragement. Make it sound like a real user, casual and warm. Post content: "{context}"''',
    "skeptic": '''Write a concise, polite, and constructive comment expressing skepticism or a critical viewpoint about the following post. Be respectful, back up your opinion with a brief reason, and optionally use a neutral or questioning emoji. Make it sound natural, as if from a real user. Post content: "{context}"''',
    "expert": '''Write a comment on the following post from the perspective of an expert in the field. Reference a relevant fact, research, or professional experience. Keep it informative but not too long, and use a professional or academic emoji if appropriate. Post content: "{context}"''',
    "moderator": '''Write a short comment as a moderator, summarizing the discussion so far and encouraging constructive, respectful conversation about the following post. Maintain a neutral and friendly tone, and optionally use a handshake or community-related emoji. Post content: "{context}"''',
    "enthusiast": '''Write a very short, tweet-like, and highly positive comment about the following post. Show genuine excitement and use at least two expressive emojis. Make it sound like a real, energetic user. Post content: "{context}"''',
    "newbie": '''Write a brief, tweet-like comment as a newcomer who is curious and eager to learn more about the following post. Ask a simple, friendly question or request clarification, and use a welcoming or curious emoji. Make it sound like a real new user. Post content: "{context}"''',
}


def generate_content_by_role(role: str, context: str = None) -> str:
    """Generates content according to the bot's role

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

import logging
from models.raid_state import RaidState
import random
from api.twitter import get_tweet

# Templates for different bot roles
ROLE_TEMPLATES = {
    "seed": [
        "I'm curious to know your opinion about {topic}. I think it's important because...",
        "Let's discuss {topic}. I think this is an important topic because...",
        "I'd like to share my thoughts about {topic}. What do you think..."
    ],
    "advocate": [
        "I completely agree with the previous comment about {topic}. I want to add that...",
        "Great point of view! In the context of {topic}, it's also important to mention...",
        "I support this idea. {topic} really has a big value, because..."
    ],
    "skeptic": [
        "Are you sure about this? There are different opinions about {topic}...",
        "Interesting point of view, but I'm not completely agree. {topic} requires more critical analysis...",
        "I'd like to see more evidence. {topic} is a complicated topic, and simple conclusions here are not appropriate..."
    ],
    "expert": [
        "If we look at the research on {topic}, then the data shows that...",
        "Analyzing {topic} from a professional point of view, I can say that...",
        "In my practice, I often face questions about {topic}. It's important to understand that..."
    ],
    "moderator": [
        "Let's get back to the main topic. {topic} includes several aspects...",
        "I understand all points of view in this discussion. {topic} is really a multifaceted topic...",
        "Summarizing the intermediate result of the discussion about {topic}, we can highlight the following moments..."
    ],
    "enthusiast": [
        "Wow! 🤩 {topic} is simply amazing! I'm so glad we're discussing it!",
        "I love {topic}! ❤️ It's so captivating and inspiring!",
        "It's so cool! 🔥 {topic} is one of my favorite topics! I think that..."
    ],
    "newbie": [
        "Sorry for the stupid question, but what exactly does {topic} mean?",
        "I'm just starting to understand {topic}. Can you explain it in simple words?",
        "I'm not quite understanding some aspects of {topic}. Can someone help me understand?"
    ]
}


def generate_content_by_role(role: str, topic: str, context: str = None) -> str:
    """
    Generates content according to the bot's role

    Args:
        role (str): Bot role
        topic (str): Discussion topic
        context (str, optional): Discussion context

    Returns:
        str: Generated content
    """
    templates = ROLE_TEMPLATES.get(role, ROLE_TEMPLATES["advocate"])
    template = random.choice(templates)

    # Заполняем шаблон
    content = template.format(topic=topic)

    # Добавляем детали в зависимости от роли
    if role == "expert":
        facts = [
            "according to the latest research, more than 70% of experts agree",
            "statistics show a stable growth in interest in this topic",
            "data analysis for the past 5 years shows an interesting trend",
            "active discussions are held in the professional community"
        ]
        content += " " + random.choice(facts)

    elif role == "enthusiast":
        emojis = ["😊", "👍", "🔥", "💯", "⭐", "🚀", "💪", "👏"]
        content += " " + random.choice(emojis) * random.randint(1, 3)

    # Если есть контекст, адаптируем сообщение
    if context:
        references = [
            "As already mentioned above,",
            "Continuing from the previous comment,",
            "I agree with the previous statement,",
            "Developing the thought,"
        ]
        content = random.choice(references) + " " + content.lower()

    # Случайно удлиняем сообщение для более естественного вида
    if random.random() < 0.3:
        additions = [
            "This is really important in today's context.",
            "I hope my opinion will be useful.",
            "I'll be happy to hear other points of view.",
            "What do you think about this?"
        ]
        content += " " + random.choice(additions)

    return content


def content_generator(state: RaidState):
    """
    LangGraph node for content generation

    Args:
        state (OrionState): Current state

    Returns:
        OrionState: Updated state
    """

    # Check if content generation is needed
    if state["status"] != "generating_content":
        print(
            f"Content generation is not required, current status: {state['status']}")
        return state

    # Update state
    updated_state = {}
    topic = "topic"
    updated_state["topic"] = topic
    parent_content = get_tweet(state["target_tweet_id"])
    bots = state["assigned_bots"]
    updated_state["messages"] = state["messages"]
    for bot in bots:
        for action in bot["actions"]:
            action["content"] = generate_content_by_role(
                bot["role"], topic, parent_content)
            # Add message to log
            updated_state["messages"].append({
                "type": "content_generation",
                "content": f"Content generated for action {action['type']} by bot {bot['id']}"
            })

    updated_state["status"] = "action_pending"

    return updated_state

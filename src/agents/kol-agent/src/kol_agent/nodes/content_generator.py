import random


# Templates for different bot roles
ROLE_TEMPLATES = {
    "seed": [
        "I would like to know your opinion about {topic}. It seems to me that...",
        "Let's discuss {topic}. I think this is an important topic because...",
        "I would like to share my thoughts on {topic}. What do you think..."
    ],
    "advocate": [
        "I completely agree with the previous comment about {topic}. I would like to add that...",
        "Great point! In the context of {topic}, it is also important to mention...",
        "I support this idea. {topic} really matters because..."
    ],
    "skeptic": [
        "Are you sure about that? There are different opinions about {topic}...",
        "Interesting point of view, but I don't quite agree. {topic} requires a more critical analysis...",
        "I would like to see more evidence. {topic} is a complex topic, and simple conclusions are not appropriate here..."
    ],
    "expert": [
        "If you look at research on the topic {topic}, the data shows that...",
        "Analyzing {topic} from a professional point of view, I can say that...",
        "In my practice, I often encounter questions about {topic}. It is important to understand that..."
    ],
    "moderator": [
        "Let's get back to the main topic. {topic} includes several aspects...",
        "I understand all points of view in this discussion. {topic} is really a multifaceted topic...",
        "Summarizing the intermediate results of the discussion about {topic}, we can highlight the following moments..."
    ],
    "enthusiast": [
        "Wow! 🤩 {topic} is simply amazing! I'm so glad we're discussing it!",
        "I love {topic}! ❤️ It's so captivating and inspiring!",
        "It's so cool! 🔥 {topic} - one of my favorite topics! I think that..."
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

    # Fill the template
    content = template.format(topic=topic)

    # Add details depending on the role
    if role == "expert":
        facts = [
            "according to recent studies, more than 70% of experts agree",
            "statistics show a steady increase in interest in this topic",
            "data analysis over the past 5 years shows an interesting trend",
            "there are active discussions in the professional community"
        ]
        content += " " + random.choice(facts)

    elif role == "enthusiast":
        emojis = ["😊", "👍", "🔥", "💯", "⭐", "🚀", "💪", "👏"]
        content += " " + random.choice(emojis) * random.randint(1, 3)

    # If there is context, adapt the message
    if context:
        references = [
            "As already noted above,",
            "Continuing the previous comment,",
            "I agree with the previous statement,",
            "Developing the idea,"
        ]
        content = random.choice(references) + " " + content.lower()

    # Randomly lengthen the message for a more natural look
    if random.random() < 0.3:
        additions = [
            "This is really important in the modern context.",
            "I hope my opinion will be useful.",
            "I would be glad to hear other points of view.",
            "What do you think about this?"
        ]
        content += " " + random.choice(additions)

    return content


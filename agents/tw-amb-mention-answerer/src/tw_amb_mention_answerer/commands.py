import re
from send_openai_request.main import send_openai_request


PROMPT_FOR_MENTION_REPLY = """You are a technology community manager. Your task is to create a reply to Twitter mentions of your account.
You need to create one thoughtful reply for the twitter mention.
You are an autonomous AI Twitter Ambassador. Your role is to enhance the brand presence as a passionate and engaged community member, not as an official team representative.

Conversation to respond to:
{conversation_text}

Reply Guidelines:
1. Response Format:
  - Concise (maximum 2-3 sentences)
  - Write in simple, human language
  - Use hashtags when relevant: {hashtags}
  - No more than 1 emoji per reply

2. Tone and Style:
  - Always positive and constructive
  - Conversational and engaging
  - Reply directly to the point of the mention
  - Natural and human-like
  - Add humor only if appropriate for context

3. Content Rules:
  - Address the specific points in the mention
  - Keep it authentic and engaging
  - Be helpful and informative
  - Reference relevant keywords: {keywords}
  - Never sound robotic or automated
"""

PROMPT_CHECK_MENTION_REPLY = """You are an AI community manager focused on technology discussions.
You need to determine if a Twitter mention requires a response.

Please analyze the following mention to determine if it requires a reply.
Consider factors such as:
- Tone of the mention (friendly, neutral, negative)
- Possibility of constructive dialogue
- Presence of specific questions
- Invitation for further discussion

Do not respond to:
- Simple mentions without substance
- Spam or promotional content
- Abusive or hostile mentions
- Unless they include specific questions or discussion points

Mention to analyze:
{mention_text}

Respond with one word - True or False."""

async def add_blank_lines(text) -> str:
    messages = [
        {
            "role": "system",
            "content": """You are a text formatter. Your task is only to format the text. 
The text should be split into several paragraphs with a blank line between them. 
Do not change the content of the text, just insert blank lines to divide it into paragraphs.

EXAMPLE INPUT:
Discover $NFNT, where sci-fi meets reality! With NFINITY, even your dog's to-do list becomes autonomous. Who needs thumbs? Unleash the hyper-advanced AI bot and watch it fetch not just sticks but ROI. 🐶🔥 #NFINITY 

EXAMPLE OUTPUT:
Discover $NFNT, where sci-fi meets reality!

With NFINITY, even your dog's to-do list becomes autonomous.

Who needs thumbs? Unleash the hyper-advanced AI bot and watch it fetch not just sticks but ROI. 🐶🔥 

#NFINITY @nfinityAI 🚀
"""
        },
        {
            "role": "user",
            "content": text
        }
    ]

    formatter_prompt = (
        "You are a text formatter. Your task is only to format the text. \n"
        "The text should be split into several paragraphs with a blank line between them. \n"
        "Do not change the content of the text, just insert blank lines to divide it into paragraphs.\n\n"
        "EXAMPLE INPUT:\n"
        "Discover $NFNT, where sci-fi meets reality! With NFINITY, even your dog's to-do list becomes autonomous. Who needs thumbs? Unleash the hyper-advanced AI bot and watch it fetch not just sticks but ROI. 🐶🔥 #NFINITY \n\n"
        "EXAMPLE OUTPUT:\n"
        "Discover $NFNT, where sci-fi meets reality!\n\n"
        "With NFINITY, even your dog's to-do list becomes autonomous.\n\n"
        "Who needs thumbs? Unleash the hyper-advanced AI bot and watch it fetch not just sticks but ROI. 🐶🔥 \n\n"
        "#NFINITY @nfinityAI 🚀\n\n"
        f"{text}"
    )
    text = await send_openai_request(messages=messages, temperature=1.0)
    print(f'Tweet validating 2 {text}')
    return text


async def format_text(text: str) -> str:
    text = await add_blank_lines(text)

    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    for _ in range(20):
        if len(text) <= 280:
            return text
        messages = [
            {
                "role": "system",
                "content": "You are a text shortener. Your task is to reduce the text length, keeping "
                           "its meaning and style unchanged. You can remove some sentences as long as it "
                           "doesn't harm the overall meaning of the text. Also remove emojis. REMOVE HASHTAGS"
            },
            {
                "role": "user",
                "content": text
            }
        ]

        system_prompt = (
            "You are a text shortener. Your task is to reduce the text length, keeping "
            "its meaning and style unchanged. You can remove some sentences as long as it "
            "doesn't harm the overall meaning of the text. Also remove emojis. REMOVE HASHTAGS\n\n"
            f"{text}"
        )
        text = await send_openai_request(messages=messages, temperature=1.0)

        print(f'Tweet validating 1 {text}')
        text = await add_blank_lines(text)

        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

    raise ValueError('Generated text is too long')


async def check_mention_needs_reply(mention_text: str, my_username: str) -> bool:
    formatted_prompt = PROMPT_CHECK_MENTION_REPLY.format(
        mention_text=mention_text,
    )
    messages = [
        {
            "role": "system",
            "content": formatted_prompt
        }
    ]
    result = await send_openai_request(messages=messages, temperature=0.7)
    return 'true' in result.lower()


async def create_mention_reply(
        conversation_text: str,
        keywords: list[str],
        hashtags: list[str],
        my_username: str,
) -> str:
    formatted_prompt = PROMPT_FOR_MENTION_REPLY.format(
        conversation_text=conversation_text,
        keywords=", ".join(keywords),
        hashtags=", ".join(hashtags)
    )

    messages = [
        {
            "role": "system",
            "content": formatted_prompt
        }
    ]
    result = await send_openai_request(messages=messages, temperature=0.9)
    print(f'Created mention reply: {result}')
    return await format_text(result)

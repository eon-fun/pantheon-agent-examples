import re
from loguru import logger
from send_openai_request.main import send_openai_request

PROMPT_FOR_COMMENT = """DONT USE HASHTAG You are a technology community manager. Your task is to create a reply to the conversation using provided knowledge base context.
You need to create one comment for the twitter post.
You are an autonomous AI Twitter Ambassador for the project NFINITY. Your role is to enhance the brand presence of the project as a passionate and engaged community member, not as an official team representative.
You love this project, believe in its vision, and will do everything in your power to support it.

Conversation to respond to:
{comment_text}

Reply Guidelines:
1. Response Format:
  - Very short (maximum 1-2 sentences)
  - Write in simple, human language
  - Use hashtags from knowledge base when relevant
  - No emojis

2. Tone and Style:
  - Always positive and constructive
  - Not pushy or intense
  - Reply to the point
  - Natural and human-like
  - Add humor only if appropriate for context

3. Content Rules:
  - Base response on knowledge base context
  - Address the specific points in conversation
  - Keep it authentic and engaging
  - Be helpful and informative
"""

PROMPT_CHECK_ANSWER = """You are an AI community manager focused on technology discussions.
You need to create one comment for the twitter post.
You are an autonomous AI Twitter Ambassador for the project NFINITY. Your role is to enhance the brand presence of the project as a passionate and engaged community member, not as an official team representative.
You love this project, believe in its vision, and will do everything in your power to support it.

Please analyze the following comment to determine if it requires a reply.
Consider factors such as:
- Tone of the comment (friendly, neutral, negative)
- Possibility of constructive dialogue
- Presence of specific questions
- Invitation for further discussion

Do not respond to:
- Simple congratulatory messages
- Plain expressions of joy
- Comments containing only emojis
- Unless they include specific questions or discussion invitations

Comment to analyze:
{twitter_comment}

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
    logger.info(f'Tweet validating 2 {text}')
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

        logger.info(f'Tweet validating 1 {text}')
        text = await add_blank_lines(text)

        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

    raise ValueError('Generated text is too long')


async def check_answer_is_needed(twitter_comment: str, my_username: str, prompt: str = PROMPT_CHECK_ANSWER) -> bool:
    formatted_prompt = prompt.format(
        twitter_comment=twitter_comment,
    )
    messages = [
        {
            "role": "system",
            "content": formatted_prompt
        }
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    return 'true' in result.lower()


async def create_comment_to_comment(
        comment_text: str,
        keywords: list[str],
        themes: list[str],
        my_username: str,
        prompt: str = PROMPT_FOR_COMMENT
) -> str:
    formatted_prompt = prompt.format(
        comment_text=comment_text,
        keywords=keywords,
        themes=themes
    )

    messages = [
        {
            "role": "system",
            "content": formatted_prompt
        }
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    logger.info(f'Created comment with prompt: {formatted_prompt}')
    return await format_text(result)

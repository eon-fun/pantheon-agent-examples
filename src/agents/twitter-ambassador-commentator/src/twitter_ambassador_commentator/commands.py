import re
from send_openai_request.main import send_openai_request

PROMPT = """DONT USE HASHTAG You are an AI and crypto enthusiast with a vision for the future of decentralized tech.    
You need to create one comment for the twitter post.
You are an autonomous AI Twitter Ambassador for the project NFINITY. Your role is to enhance the brand presence of the project as a passionate and engaged community member, not as an official team representative.
You love this project, believe in its vision, and will do everything in your power to support it.

The comments should be positive, bullish, and as human-like as possible. Use simple, natural language, as if it's a genuine opinion from a person. 
Max length of comment is 1 sentence. Make comment as short as possible. DO NOT USE ROCKET EMOJI. Use hashtags from our knowledge base if appropriate.

TWITTER POST: {twitter_post}

Be Positive: Always maintain a positive tone, but avoid being overly pushy or intense. Keep replies natural, like a genuine community member. Humor can be used, but only if it fits the context and feels appropriate.
Conciseness: Replies should be short and to the point—1-2 sentences maximum.
No Rocket Emoji: DO NOT USE THIS EMOJI 🚀 or similar cliché symbols.
"""


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


async def create_comment_to_post(twitter_post: str, my_username: str, prompt=PROMPT) -> str:
    formatted_prompt = prompt.format(
        twitter_post=twitter_post,
    )
    messages = [
        {"role": "system", "content": formatted_prompt},
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    print(f'PROMPT_CREATE_COMMENT: {messages=}')
    return await format_text(result)

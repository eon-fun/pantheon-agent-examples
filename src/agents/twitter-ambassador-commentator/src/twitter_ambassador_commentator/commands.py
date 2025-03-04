from send_openai_request.main import send_openai_request


async def create_comment_to_post(twitter_post: str, my_username: str, prompt='') -> str:
    messages = [
        {"role": "system", "content": prompt},
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    print(f'PROMPT_CREATE_COMMENT: {messages=}')
    return result

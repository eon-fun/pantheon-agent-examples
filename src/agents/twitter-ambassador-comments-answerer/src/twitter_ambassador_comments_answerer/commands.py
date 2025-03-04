from send_openai_request.main import send_openai_request

from typing import List


async def check_answer_is_needed(twitter_comment: str, my_username: str, prompt: str = "") -> bool:
    messages = [
        {
            "role": "system",
            "content": prompt
        }
    ]
    result = await send_openai_request(messages=messages, temperature=1.0)
    return 'true' in result.lower()


async def create_comment_to_comment(
        comment_text: str,
        keywords: List[str],
        themes: List[str],
        my_username: str,
        prompt: str = ""
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
    print(f'Created comment with prompt: {formatted_prompt}')
    return result

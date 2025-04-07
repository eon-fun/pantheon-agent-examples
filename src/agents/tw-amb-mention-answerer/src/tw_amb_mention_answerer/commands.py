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
    return result

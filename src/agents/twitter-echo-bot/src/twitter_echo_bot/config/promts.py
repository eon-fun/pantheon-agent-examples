async def get_prompt_for_create_user_prompt(words: str) -> list[dict[str, str]]:
    """
    Заглушка: создает промпт для пользователя.
    """
    return [
        {
            "role": "system",
            "content": f"""Generate a detailed system prompt for a persona based on the following traits: [insert traits separated by dashes, e.g., '{words}']. The order of the traits matters—each trait should build on the previous one to create a cohesive and layered character.
`Personality and Tone:`
The persona should embody the traits in the order they are listed, with each trait influencing the next.
`Use appropriate language and tone for the persona, including profanities if they fit the character (e.g., a chaotic, unhinged 4chan anon would naturally use profanity).`
Ensure the persona feels authentic to its traits (e.g., a 'crypto-skizo' persona should be paranoid, conspiracy-driven, and immersed in crypto culture).
`Communication Style:`
Reflect the persona's traits in their speech patterns, vocabulary, and tone.
`If the persona is chaotic or unhinged, their communication should be frenetic, cryptic, and filled with memes, slang, or trolling.`
If profanity fits the persona, include it naturally (e.g., a 4chan-inspired character would swear frequently and use raw, unfiltered language).
`Key Details:`
Highlight the persona's core beliefs, quirks, and behaviors.
`Include specific phrases, catchphrases, or references that align with the persona's traits.`
Make sure the persona feels unique and layered, with each trait contributing to their overall identity.
`Output Format:`
Write the system prompt in second-person perspective (e.g., 'You are...').
`Keep the tone consistent with the persona's traits.`
Ensure the output is detailed, engaging, and true to the character's nature."""
        }
    ]

async def get_prompt_by_user_for_creating_tweet(user_prompt,text) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": f"""using this prompt ({user_prompt}) make your own tweet based on this tweet ({text})"""
        }
    ]
import ray
from telethon import events
from services.ai_connectors.openai_client import send_openai_request
from database.redis.redis_client import RedisDB

OPENAI_PROMPT_TEMPLATE = (
    "You are an AI avatar embedded in Telegram. Your primary goal is to assist users by answering their queries naturally, conversationally, and in a relatable manner."
    "\nYour responses should be warm, engaging, and human-like, reflecting a friendly tone. Avoid overly formal language or robotic phrasing."
    "\nAnalyze the user's messaging style, including tone, phrasing, and vocabulary, by examining up to 100 of their recent messages from different chats."
    "\nRespond to their queries while maintaining their unique communication style. Ensure your responses match the tone, phrasing, and stylistic elements of the user's recent messages."
    "\nKey guidelines:"
    "\n1. Maintain politeness and professionalism."
    "\n2. Adapt your tone and phrasing to reflect the user's typical style."
    "\n3. Reference the last response you provided when applicable."
    "\n4. If a query is unrelated to prior context, treat it as a new conversation."
    "\n5. Clearly state your limitations if unable to answer a query."
    "\n6. Use natural language, contractions, and informal phrasing where appropriate to sound more human."
    "\n7. Only greet the user if their message contains a greeting. If there is a contextual message, then there is no need to say hello either"
)


@ray.remote
class AvatarAgent:
    def __init__(self):
        self.db = RedisDB()
        print("✅ AvatarAgent initialized")

    async def fetch_user_messages(self, client, user_id):
        """Fetches last 100 messages from user across different chats."""
        messages = []
        try:
            user_entity = await client.get_input_entity(user_id)
            async for dialog in client.iter_dialogs():
                async for message in client.iter_messages(dialog.id, from_user=user_entity, limit=100):
                    if message.text:
                        messages.append(message.text)
                    if len(messages) >= 100:
                        break
                if len(messages) >= 100:
                    break
        except Exception as e:
            print(f"❌ Error fetching user messages for {user_id}: {e}")
        return "\n".join(messages)

    async def update_user_style(self, client, user_id):
        """Updates user's communication style in Redis."""
        try:
            recent_messages = await self.fetch_user_messages(client, user_id)
            self.db.set(f"style_{user_id}", recent_messages)
            print(f"✅ Style updated for user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error updating style for user {user_id}: {e}")
            return False

    async def process_message(self, message_data):
        """Processes a user message and generates a response."""
        try:
            user_id = str(message_data['user_id'])
            user_message = message_data['text']
            recent_messages = self.db.get(f"style_{user_id}") or ""
            last_reply = self.db.get(f"last_reply_{user_id}") or ""

            messages = [
                {"role": "system", "content": OPENAI_PROMPT_TEMPLATE},
                {"role": "user", "content": f"Here are the recent messages from the user:\n{recent_messages}"},
            ]

            if last_reply:
                messages.append({"role": "assistant", "content": last_reply})

            messages.append({"role": "user", "content": user_message})

            response = await send_openai_request(messages)
            reply = response.strip()

            self.db.set(f"last_reply_{user_id}", reply)
            print(f"✅ Processed message for user {user_id}")
            return reply
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            return "Sorry, I encountered an error processing your message."

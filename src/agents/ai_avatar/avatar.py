import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from services.ai_tools.openai_client import send_openai_request
from database.redis.redis_client import RedisDB

# Конфигурация
API_ID = "26012476"
API_HASH = "d0ba6cd225c5dea4d2f7eb717adbeaac"
SESSION_NAME = "ai_avatar_session"
OPENAI_PROMPT_TEMPLATE = (
    "You are an AI avatar embedded in Telegram. Your primary goal is to assist users by answering their queries naturally, conversationally, and in a relatable manner."
    "\nYour responses should be warm, engaging, and human-like, reflecting a friendly tone. Avoid overly formal language or robotic phrasing."
    "\nAnalyze the user's messaging style, including tone, phrasing, and vocabulary, by examining up to 100 of their recent messages from different chats."
    "\nRespond to their queries while maintaining their unique communication style. Ensure your responses match the tone, phrasing, and stylistic elements of the user’s recent messages."
    "\nKey guidelines:"
    "\n1. Maintain politeness and professionalism."
    "\n2. Adapt your tone and phrasing to reflect the user’s typical style."
    "\n3. Reference the last response you provided when applicable."
    "\n4. If a query is unrelated to prior context, treat it as a new conversation."
    "\n5. Clearly state your limitations if unable to answer a query."
    "\n6. Use natural language, contractions, and informal phrasing where appropriate to sound more human."
    "\n7. Only greet the user if their message contains a greeting. If there is a contextual message, then there is no need to say hello either"
)

# Инициализация Redis
redis_client = RedisDB()

# Инициализация Telethon клиента
client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)


async def fetch_user_messages():
    """Загружает последние 100 сообщений пользователя из разных чатов."""
    messages = []
    try:
        user_entity = await client.get_input_entity(client._self_id)  # Преобразуем user_id в InputPeer
        async for dialog in client.iter_dialogs():
            async for message in client.iter_messages(dialog.id, from_user=user_entity, limit=100):
                messages.append(message.text)
                if len(messages) >= 100:
                    break
            if len(messages) >= 100:
                break
    except ValueError as e:
        print(f"Ошибка получения сущности пользователя {client._self_id}: {e}")
    return "\n".join(filter(None, messages))


async def handle_new_style_command(event):
    """Обрабатывает команду /new_style для обновления сообщений стиля пользователя."""
    try:
        # Обновляем сообщения стиля пользователя
        recent_messages = await fetch_user_messages()
        redis_client.set(client._self_id, recent_messages)
        await event.reply("Контекст стиля общения успешно обновлен!")
    except Exception as e:
        print(f"Ошибка обновления стиля: {e}")
        await event.reply("Произошла ошибка при обновлении стиля общения.")


async def handle_user_message(event):
    user_id = str(event.sender_id)  # Уникальный идентификатор пользователя
    user_message = event.text.strip()

    # Загружаем последние сообщения пользователя для анализа стиля
    recent_messages = await fetch_user_messages()

    # Загружаем последний ответ из Redis
    last_reply = redis_client.get(user_id) or ""

    # Формируем запрос к OpenAI с учетом стиля пользователя и последнего ответа
    print(recent_messages)
    messages = [
        {"role": "system", "content": OPENAI_PROMPT_TEMPLATE},
        {"role": "user", "content": f"Here are the recent messages from the user:\n{recent_messages}"},
    ]
    if last_reply:
        messages.append({"role": "assistant", "content": last_reply})
    messages.append({"role": "user", "content": user_message})

    try:
        # Обращение к OpenAI API
        response = await send_openai_request(messages)
        reply = response.strip()

        # Сохранение текущего ответа в Redis
        redis_client.set(user_id, reply)

        # Отправка ответа пользователю
        await event.reply(reply)
    except Exception as e:
        print(f"Ошибка обработки сообщения: {e}")
        await event.reply("Произошла ошибка при обработке вашего запроса.")


@client.on(events.NewMessage(pattern='/new_style'))
async def on_new_style_command(event):
    await handle_new_style_command(event)


@client.on(events.NewMessage)
async def on_new_message(event):
    if not event.out:  # Игнорируем исходящие сообщения
        await handle_user_message(event)


async def main():
    print("Запуск AI-аватара Telegram")

    try:
        await client.connect()

        if not await client.is_user_authorized():
            print("Требуется авторизация")
            phone = input("Введите ваш номер телефона: ").strip()

            try:
                await client.send_code_request(phone)
                code = input("Введите код из SMS: ").strip()
                await client.sign_in(phone=phone, code=code)
            except SessionPasswordNeededError:
                print("Требуется облачный пароль")
                password = input("Введите пароль: ").strip()
                await client.sign_in(password=password)
            except PhoneCodeInvalidError:
                print("Неверный код. Попробуйте снова.")

        print("Успешное подключение!")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from telethon import TelegramClient, events, functions
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberUnoccupiedError
from telethon.tl.types import Message, PeerUser, PeerChannel, PeerChat, InputPeerEmpty
from services.ai_tools.openai_client import send_openai_request
from database.redis.redis_client import RedisDB
import json

# Конфигурация
API_ID = ""  # Подставить от нужного акка
API_HASH = ""  # Подставить от нужного акка
SESSION_NAME = "my_telegram_session"
REDIS_MESSAGES_KEY = "telegram_messages"
BOT_COMMAND = "/summary"

PROMPT = (
    "You are an assistant summarizing messages in a chat. "
    "Your task is to create a brief summary of what each user discussed without answering any questions. "
    "For example: \n"
    "@username mentioned something about topic X.\n"
    "@another_user brought up another topic Y.\n"
    "Also note if someone was mentioned or replied to in the chat and include the chat name. "
    "Do not provide solutions, just summarize the content of the messages concisely."
)

# Инициализация Redis
db = RedisDB()

# Инициализация Telethon клиента
client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)


async def collect_messages(event):
    """Сохраняет только непрочитанные сообщения, упоминания или ответы в Redis."""
    if event.text and isinstance(event.message, Message):
        if not event.message.out or event.message.mentioned or event.message.reply_to:
            sender = await event.get_sender()
            chat = await event.get_chat()
            chat_id = chat.id
            chat_name = chat.title if hasattr(chat, 'title') and chat.title else "Личный чат"
            username = sender.username if sender and sender.username else None
            name = f"@{username}" if username else (sender.first_name if sender and sender.first_name else "Unknown")

            # Определяем тип действия: упоминание или ответ
            action = "написал"
            if event.message.mentioned:
                action = "упомянул"
            elif event.message.reply_to:
                action = "ответил"

            message_id = str(event.message.id)

            message_data = {
                "id": message_id,
                "text": event.text,
                "sender_username": name,
                "action": action,
                "chat_name": chat_name,
                "chat_id": chat_id,
                "timestamp": event.message.date.timestamp()
            }
            db.add_to_sorted_set(REDIS_MESSAGES_KEY, int(message_data["timestamp"]), json.dumps(message_data))
            print(f"✅ Сообщение сохранено из чата '{chat_name}': {event.text[:50]}...")


async def clean_read_messages():
    """Проверяет и удаляет прочитанные сообщения из Redis."""
    try:
        dialogs = await client(functions.messages.GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=100,
            hash=0
        ))

        messages = db.get_sorted_set(REDIS_MESSAGES_KEY)
        updated_messages = []

        for msg in messages:
            msg_data = json.loads(msg)
            chat_id = msg_data["chat_id"]
            message_id = int(msg_data["id"])

            # Находим диалог для текущего сообщения
            dialog = next((d for d in dialogs.dialogs if (
                    isinstance(d.peer, PeerUser) and d.peer.user_id == chat_id) or (
                                   isinstance(d.peer, PeerChannel) and d.peer.channel_id == chat_id) or (
                                   isinstance(d.peer, PeerChat) and d.peer.chat_id == chat_id)
                           ), None)

            if dialog and dialog.read_inbox_max_id >= message_id:
                print(f"🗑 Удаляем прочитанное сообщение ID {message_id} из чата {chat_id}.")
            else:
                updated_messages.append(msg)

        # Обновляем Redis
        db.delete(REDIS_MESSAGES_KEY)
        for msg in updated_messages:
            db.add_to_sorted_set(REDIS_MESSAGES_KEY, json.loads(msg)["timestamp"], msg)

    except Exception as e:
        print(f"❌ Ошибка очистки прочитанных сообщений: {e}")


async def generate_summary():
    """Генерирует сводку из сообщений, хранящихся в Redis."""
    await clean_read_messages()

    messages = db.get_sorted_set(REDIS_MESSAGES_KEY)
    if not messages:
        return "Нет сообщений для обработки."

    # Преобразуем список сообщений в единый текст с указанием username, действия и названия чата
    combined_text = "\n".join([
        f"[{json.loads(msg)['chat_name']}] {json.loads(msg)['sender_username']} {json.loads(msg)['action']}: {json.loads(msg)['text']}"
        for msg in messages
    ])

    # Очищаем Redis после генерации сводки
    db.delete(REDIS_MESSAGES_KEY)

    # Формируем запрос к OpenAI
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": combined_text}
    ]

    try:
        summary = await send_openai_request(messages)
        return summary.strip()
    except Exception as e:
        return f"Ошибка обработки сводки: {e}"


@client.on(events.NewMessage(pattern=BOT_COMMAND))
async def handle_summary_command(event):
    """Обрабатывает команду /summary и отправляет сводку."""
    await event.respond("⏳ Генерация сводки, пожалуйста, подождите...")
    summary = await generate_summary()
    await event.respond(f"📋 Сводка:\n{summary}")


@client.on(events.NewMessage)
async def handle_new_message(event):
    """Собирает новые сообщения."""
    await collect_messages(event)


async def main():
    print("🚀 Запуск клиента Telethon")
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("⏳ Требуется авторизация")
            phone = input("Введите ваш номер телефона: ").strip()
            try:
                await client.send_code_request(phone)
                code = input("Введите код из SMS: ").strip()
                try:
                    await client.sign_in(phone=phone, code=code)
                except SessionPasswordNeededError:
                    print("🔒 Требуется облачный пароль (2FA)")
                    password = input("Введите ваш облачный пароль: ").strip()
                    await client.sign_in(password=password)
                    print("✅ Успешная авторизация с облачным паролем!")
            except PhoneCodeInvalidError:
                print("❌ Неверный код. Попробуйте снова.")
            except PhoneNumberUnoccupiedError:
                print("❌ Номер телефона не зарегистрирован в Telegram.")
        print("✅ Успешно подключено!")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

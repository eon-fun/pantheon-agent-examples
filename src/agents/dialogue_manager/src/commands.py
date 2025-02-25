from telethon import functions
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberUnoccupiedError
from telethon.tl.types import PeerUser, PeerChannel, PeerChat, InputPeerEmpty

from config import telethon_client as client


async def get_read_messages_data(client):
    try:
        dialogs = await client(functions.messages.GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=100,
            hash=0
        ))

        return [
            {
                "chat_id": (
                    d.peer.user_id if isinstance(d.peer, PeerUser)
                    else d.peer.channel_id if isinstance(d.peer, PeerChannel)
                    else d.peer.chat_id if isinstance(d.peer, PeerChat)
                    else None
                ),
                "max_id": d.read_inbox_max_id
            }
            for d in dialogs.dialogs
        ]
    except Exception as e:
        print(f"❌ Error fetching read messages: {e}")
        return []


async def telethon_auth():
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

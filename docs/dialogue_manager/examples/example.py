import asyncio
from dialogue_manager.main import DialogueManager


async def main():
    manager = DialogueManager()

    sample_msg = {
        "id": "123",
        "text": "Hello world",
        "sender_username": "@testuser",
        "action": "wrote",
        "chat_name": "Test Chat",
        "chat_id": 456,
        "timestamp": 1234567890
    }
    await manager.process_message(sample_msg)

    summary = await manager.generate_summary()
    print(f"Summary: {summary}")


asyncio.run(main())

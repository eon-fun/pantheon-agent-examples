from aiogram import types


async def handle_add_account(self, message: types.Message):
    """Handle the /add_account command."""
    try:
        accounts = message.text.split()[1:]
        if not accounts:
            await message.answer("❌ Please specify accounts to add.")
            return

        results = []
        for account in accounts:
            account = account.strip("@")
            success = await self.tweet_processor.add_account.remote(account)
            results.append(f"{'✅' if success else '❌'} @{account}")

        response = "\n".join(results)
        print(f"Adding accounts response: {response}")
        await message.answer(response)

    except Exception as e:
        error_msg = f"❌ Error adding account: {str(e)}"
        print(error_msg)
        await message.answer(error_msg)

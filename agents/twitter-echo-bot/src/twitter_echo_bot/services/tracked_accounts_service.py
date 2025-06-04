from sqlalchemy.ext.asyncio import AsyncSession
from twitter_echo_bot.DB.managers.tracked_accounts_manager import AlchemyTrackedAccountsManager


async def update_user_tracked_accounts_service(user_id: int, twitter_handle: list[str], db_session: AsyncSession):
    """Обновляет список отслеживаемых аккаунтов пользователя."""
    tr_user_manager = AlchemyTrackedAccountsManager(session=db_session)
    await tr_user_manager.add_tracked_accounts(user_id=user_id, twitter_handles=twitter_handle)
    return {"message": "Tracked accounts updated successfully."}

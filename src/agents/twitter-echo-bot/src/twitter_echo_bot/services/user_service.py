from sqlalchemy.ext.asyncio import AsyncSession

from twitter_echo_bot.DB.managers.users_manager import AlchemyUsersManager
from twitter_echo_bot.DB.models.users_models import PGUser


async def get_user_service(user_id: int, db_session: AsyncSession)->PGUser:
    #TODO add check is user exists
    user_manager = AlchemyUsersManager(session=db_session)
    return await user_manager.get_user_by_id(user_id=user_id)


async def create_user_service(user_data: PGUser, db_session: AsyncSession)->PGUser:
    user_manager = AlchemyUsersManager(session=db_session)
    return await user_manager.create_user(user_data=user_data)


async def update_user_service(user_data: PGUser, db_session: AsyncSession):
    user_manager = AlchemyUsersManager(session=db_session)
    return await user_manager.update_user(user_data=user_data)
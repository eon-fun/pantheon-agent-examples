from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from follow_unfollow_bot.DB.managers.user_manager import AlchemyUsersManager


async def add_user_service(session:AsyncSession,user_twitter_id: int):
    user_manager = AlchemyUsersManager(session)
    is_user_exist = await user_manager.get_user(user_twitter_id)
    if is_user_exist:
        raise HTTPException(status_code=400, detail="User already exist")

    user = await user_manager.create_user(user_twitter_id)
    return user

async def delete_user_service(session:AsyncSession,user_twitter_id: int):
    user_manager = AlchemyUsersManager(session)
    is_user_exist = await user_manager.get_user(user_twitter_id)
    if not is_user_exist:
        raise HTTPException(status_code=400, detail="User not exist")

    await user_manager.delete_user(user_twitter_id)
    return {"message": "User deleted"}
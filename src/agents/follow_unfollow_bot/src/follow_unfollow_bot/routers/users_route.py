from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from DB.managers.user_manager import AlchemyUsersManager
from DB.sqlalchemy_database_manager import get_db

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("/add")
async def add_user(user_twitter_id: int,
                   session: AsyncSession = Depends(get_db), ):
    user_manager = AlchemyUsersManager(session)
    is_user_exist = await user_manager.get_user(user_twitter_id)
    if is_user_exist:
        raise HTTPException(status_code=400, detail="User already exist")

    user = await user_manager.create_user(user_twitter_id)
    return user


@user_router.delete("/delete")
async def delete_user(user_twitter_id: int,
                      session: AsyncSession = Depends(get_db), ):
    user_manager = AlchemyUsersManager(session)
    is_user_exist = await user_manager.get_user(user_twitter_id)
    if not is_user_exist:
        raise HTTPException(status_code=400, detail="User not exist")

    await user_manager.delete_user(user_twitter_id)
    return {"message": "User deleted"}

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from twitter_echo_bot.DB.models.users_models import PGUser
from twitter_echo_bot.DB.sqlalchemy_database_manager import get_db

from twitter_echo_bot.services.user_service import get_user_service, create_user_service, update_user_service

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/get_user", response_model=PGUser)
async def get_user_route(user_id: int,
                         db_session: AsyncSession = Depends(get_db),
                         ):
    return await get_user_service(user_id=user_id, db_session=db_session)


@user_router.post("/add_user")
async def add_user_route(user_data: PGUser,
                         db_session: AsyncSession = Depends(get_db)):
    return await create_user_service(user_data=user_data, db_session=db_session)


@user_router.post("/update_user")
async def update_user_route(user_data: PGUser,
                            db_session: AsyncSession = Depends(get_db),
                            ):
    return await update_user_service(user_data=user_data, db_session=db_session)

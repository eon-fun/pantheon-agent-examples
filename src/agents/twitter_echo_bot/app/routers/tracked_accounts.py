from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from DB.sqlalchemy_database_manager import get_db
from app.services.tracked_accounts_service import update_user_tracked_accounts_service

tracked_accounts_router = APIRouter(prefix="/tracked_accounts", tags=["tracked_accounts"])


@tracked_accounts_router.post("update_tracker_accounts")
async def update_tracker_accounts_route(user_id: int,
                                        twitter_handle: List[str],
                                        db_session: AsyncSession = Depends(get_db),
                                        ):
    await update_user_tracked_accounts_service(user_id=user_id, twitter_handle=twitter_handle, db_session=db_session)
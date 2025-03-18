from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from twitter_echo_bot.DB.managers.base import BaseAlchemyManager
from twitter_echo_bot.DB.models import AlchemyPostedTweet
from datetime import datetime

class AlchemyPostedTweetsManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create_posted_tweet(self, user_id: int, source_tweet_id: str, source_account_id: int,
                                  posted_text: str):
        stmt = insert(AlchemyPostedTweet).values(
            user_id=user_id,
            source_tweet_id=source_tweet_id,
            source_account_id=source_account_id,
            is_send=False,
            posted_text=posted_text,
            posted_at=datetime.utcnow()
        ).returning(AlchemyPostedTweet)

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.fetchone()
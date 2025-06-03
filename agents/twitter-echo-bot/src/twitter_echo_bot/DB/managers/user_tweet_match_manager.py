from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from twitter_echo_bot.DB.managers.base import BaseAlchemyManager
from twitter_echo_bot.DB.models import AlchemyUserTweetMatch
from twitter_echo_bot.DB.models.user_tweet_matches_models import PGUserTweetMatch


class AlchemyUserTweetMatchManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_unprocessed_tweets(self) -> list[PGUserTweetMatch]:
        """Получает все твиты, которые ещё не были запощены (is_processed = False)."""
        result = await self.session.execute(
            select(AlchemyUserTweetMatch)
            .where(AlchemyUserTweetMatch.is_processed == False)  # Ищем только не обработанные записи
            .order_by(AlchemyUserTweetMatch.user_id.asc())  # Сортируем по айди пользователя
        )
        records = result.scalars().all()
        return [PGUserTweetMatch.from_orm(record) for record in records]

    async def mark_tweet_as_processed(self, match_id: int):
        stmt = (
            update(AlchemyUserTweetMatch)
            .where(AlchemyUserTweetMatch.id == match_id)
            .values(is_processed=True)
            .returning(AlchemyUserTweetMatch)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.fetchone()

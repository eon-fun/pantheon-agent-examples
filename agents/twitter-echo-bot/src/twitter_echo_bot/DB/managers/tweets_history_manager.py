from datetime import datetime

from services.twitter.tweetscout_requests import Tweet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twitter_echo_bot.DB.managers.base import BaseAlchemyManager
from twitter_echo_bot.DB.models import (
    AlchemyTrackedAccount,
    AlchemyTweetHistory,
    AlchemyUserTrackedAccount,
    AlchemyUserTweetMatch,
)
from twitter_echo_bot.DB.models.tweets_history_models import PGTweetHistory


class AlchemyTweetsHistoryManager(BaseAlchemyManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def add_tweets_to_history(self, tweets: list[Tweet], account_id: int):
        """Добавляет список твитов в историю отслеживаемых аккаунтов и связывает их с подписчиками.

        :param tweets: Список твитов для добавления.
        :param account_id: ID отслеживаемого аккаунта.
        """
        if not tweets:  # Проверяем, есть ли твиты
            return

        tweet_ids = {tweet.id_str for tweet in tweets}

        # Проверяем, какие tweet_id уже есть в БД
        existing_tweet_ids = {
            row[0]
            for row in await self.session.execute(
                select(AlchemyTweetHistory.tweet_id).where(AlchemyTweetHistory.tweet_id.in_(tweet_ids))
            )
        }

        # Исключаем уже существующие твиты
        new_tweets_data = [tweet for tweet in tweets if tweet.id_str not in existing_tweet_ids]

        if not new_tweets_data:
            return  # Все твиты уже есть в базе, нет смысла продолжать

        # Получаем twitter_handle по account_id
        twitter_handle = await self.session.scalar(
            select(AlchemyTrackedAccount.twitter_handle).where(AlchemyTrackedAccount.id == account_id)
        )
        if not twitter_handle:
            return  # Если не нашли, ничего не делаем

        # Получаем всех пользователей, которые следят за этим twitter_handle
        user_ids = {
            row[0]
            for row in await self.session.execute(
                select(AlchemyUserTrackedAccount.user_id).where(
                    AlchemyUserTrackedAccount.twitter_handle == twitter_handle
                )
            )
        }

        new_tweets = []
        new_matches = []

        for tweet in new_tweets_data:
            new_tweet = AlchemyTweetHistory(
                account_id=account_id,
                tweet_id=tweet.id_str,
                tweet_text=tweet.full_text,
                created_at=datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S +0000 %Y"),
            )
            new_tweets.append(new_tweet)

            for user_id in user_ids:
                new_matches.append(
                    AlchemyUserTweetMatch(
                        user_id=user_id,
                        tweet_id=tweet.id_str,
                    )
                )

        if new_tweets:
            self.session.add_all(new_tweets)

        if new_matches:
            self.session.add_all(new_matches)

        await self.session.commit()

    async def get_tweet_by_id(self, tweet_id: str) -> PGTweetHistory:
        result = await self.session.execute(select(AlchemyTweetHistory).where(AlchemyTweetHistory.tweet_id == tweet_id))
        tweet = result.scalars().one_or_none()
        return PGTweetHistory.from_orm(tweet)

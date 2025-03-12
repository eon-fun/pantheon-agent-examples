import asyncio
from collections import defaultdict
from typing import List

from DB.managers.posted_tweets_manager import AlchemyPostedTweetsManager
from DB.managers.tweets_history_manager import AlchemyTweetsHistoryManager
from DB.managers.user_tweet_match_manager import AlchemyUserTweetMatchManager
from DB.managers.users_manager import AlchemyUsersManager
from DB.models.user_tweet_matches_models import PGUserTweetMatch
from DB.models.users_models import PGUser
from DB.sqlalchemy_database_manager import get_db
from config.promts import get_prompt_by_user_for_creating_tweet
from custom_logs.custom_logs import log
from services.ai_connectors.openai_client import send_openai_request
from services.twitter.actions.create_post import post_tweet
from services.twitter.auth_client import TwitterAuthClient


class CreateTweetsService:
    def __init__(self, ):
        pass

    async def get_unprocessed_tweets(self, ):
        """
        Получает все твиты, которые не были отправлены.
        """
        async for session in get_db():
            user_tweet_match_manager = AlchemyUserTweetMatchManager(session=session)
            data = await user_tweet_match_manager.get_unprocessed_tweets()

            return data

    async def get_users_promt(self, user_id: int) -> PGUser:
        async for session in get_db():
            user_manager = AlchemyUsersManager(session)
            user_data = await user_manager.get_user_by_id(user_id)
            return user_data

    async def create_tweet_for_user(self, user_data: PGUser, tweet_data: PGUserTweetMatch):
        async for session in get_db():
            tweet_history_manager = AlchemyTweetsHistoryManager(session=session)
            orig_tweet_data = await tweet_history_manager.get_tweet_by_id(tweet_data.tweet_id)
            tweet_text = orig_tweet_data.tweet_text
            text_for_tweet = await send_openai_request(
                await get_prompt_by_user_for_creating_tweet(user_prompt=user_data.prompt, text=tweet_text))
            posted_tweets_manager = AlchemyPostedTweetsManager(session=session)
            await posted_tweets_manager.create_posted_tweet(user_id=user_data.id, source_tweet_id=tweet_data.tweet_id,
                                                            source_account_id=orig_tweet_data.account_id,
                                                            posted_text=text_for_tweet)
            await post_tweet(access_token=await TwitterAuthClient.get_access_token(str(user_data.id)),
                             tweet_text=text_for_tweet)

            user_tweet_match_manager = AlchemyUserTweetMatchManager(session=session)
            await user_tweet_match_manager.mark_tweet_as_processed(match_id=tweet_data.id)

    async def process_unprocessed_tweets(self, data: List[PGUserTweetMatch]):
        grouped_tweets = defaultdict(list)
        for record in data:
            grouped_tweets[record.user_id].append(record)

        # Преобразуем в список списков
        return list(grouped_tweets.values())

    async def start(self):
        log.info("Создание твитов для пользователей.")
        data = await self.get_unprocessed_tweets()
        sorted_data = await self.process_unprocessed_tweets(data)
        for data in sorted_data:
            user_id = data[0].user_id
            user_data = await self.get_users_promt(user_id)
            for single_data in data:
                await self.create_tweet_for_user(user_data, single_data)


async def main():
    service = CreateTweetsService()
    data = await service.start()
    print(data)


if __name__ == '__main__':
    asyncio.run(main())

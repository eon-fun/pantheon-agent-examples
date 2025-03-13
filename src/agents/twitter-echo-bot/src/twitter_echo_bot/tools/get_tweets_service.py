import asyncio
from typing import List, Dict, Any

from twitter_echo_bot.DB.managers.tracked_accounts_manager import AlchemyTrackedAccountsManager
from twitter_echo_bot.DB.managers.tweets_history_manager import AlchemyTweetsHistoryManager
from twitter_echo_bot.DB.managers.users_manager import AlchemyUsersManager
from twitter_echo_bot.DB.models.tracked_accounts_models import PGTrackedAccount
from twitter_echo_bot.DB.sqlalchemy_database_manager import get_db
from twitter_echo_bot.config.promts import get_prompt_for_create_user_prompt
from agents_tools_logger.main import log
from send_openai_request.main import send_openai_request
from tweetscout_utils.main import fetch_user_tweets, Tweet


class TwitterCollectorClient:
    async def get_new_tweets(self, twitter_handle: str) -> List[Tweet]:
        """
        Заглушка: получает новые твиты для заданного аккаунта.
        В реальной реализации здесь будет вызов API Twitter.
        """
        # TODO: Реализовать получение твитов через API Twitter.
        print(f"Получаем твиты для {twitter_handle}")
        tweets = await fetch_user_tweets(twitter_handle)
        log.info(f"Получено {len(tweets)} твитов для {twitter_handle}")
        return tweets

    async def save_tweets(self, tweets: List[Tweet], account_id: int):
        """
        Заглушка: обрабатывает новые твиты.
        """
        async for session in get_db():
            tweets_history_manager = AlchemyTweetsHistoryManager(session=session)
            await tweets_history_manager.add_tweets_to_history(tweets, account_id=account_id)

    async def get_all_tracked_accounts(self) -> List[PGTrackedAccount]:
        """
        Заглушка: получает все отслеживаемые аккаунты.
        """
        async for session in get_db():
            tracked_accounts_manager = AlchemyTrackedAccountsManager(session=session)
            tracked_accounts = await tracked_accounts_manager.get_all_tracked_accounts()
            return tracked_accounts

    async def start_parsing_tweets(self):
        """
        Заглушка: запускает процесс сбора твитов для заданных аккаунтов.
        """
        twitter_tracked_data = await self.get_all_tracked_accounts()
        for twitter_data in twitter_tracked_data:
            tweets = await self.get_new_tweets(twitter_data.twitter_handle)
            await self.save_tweets(tweets=tweets, account_id=twitter_data.id)

    async def validate_that_all_users_have_prompts(self):
        """
        Проверяет, что все пользователи имеют промпт.
        """

        async for session in get_db():
            user_manager = AlchemyUsersManager(session)
            users = await user_manager.get_filtered_users()
            if users:
                log.info(f"Найдено {len(users)} пользователей без промптов.")
                for user in users:
                    persona_descriptor = user.persona_descriptor
                    user_prompt = await create_user_prompt(persona_descriptor)
                    await user_manager.add_prompt_to_user(user.id, user_prompt)
                    log.info(f"Добавлен промпт для пользователя {user.username}")


async def create_user_prompt(words: str) -> str:
    """
    Заглушка: создает промпт для пользователя.
    """
    gen_prompt = await get_prompt_for_create_user_prompt(words)
    user_prompt = await send_openai_request(gen_prompt)
    return user_prompt


async def main():
    # TODO check user promt
    client = TwitterCollectorClient()
    # await client.validate_that_all_users_have_prompts()
    await client.start_parsing_tweets()


if __name__ == "__main__":
    asyncio.run(main())

"""
Модуль с mock-функциями для работы с Twitter API.
Этот модуль имитирует взаимодействие с Twitter API для тестирования.
"""
import time
import uuid
import random
import logging
from typing import Dict, Any, List, Optional


class TwitterClient:
    """
    Mock-клиент для Twitter API
    """

    def __init__(self, use_real_api: bool = False):
        """
        Инициализация Twitter клиента

        Args:
            use_real_api (bool): Флаг использования реального API (не используется в текущей реализации)
        """
        self.logger = logging.getLogger("twitter_api")
        self.use_real_api = use_real_api
        self.logger.info("Инициализация Twitter клиента (mock)")

    def post_tweet(self, content: str, bot_id: str) -> Dict[str, Any]:
        """
        Публикация твита

        Args:
            content (str): Содержание твита
            bot_id (str): ID бота, от имени которого публикуется твит

        Returns:
            Dict[str, Any]: Ответ API с информацией о твите
        """
        self.logger.info(f"Бот {bot_id} публикует твит: {content[:50]}...")
        # Имитация задержки сети
        time.sleep(0.1)

        # Генерация ID твита
        tweet_id = f"tweet_{uuid.uuid4().hex[:10]}"

        return {
            "id": tweet_id,
            "content": content,
            "bot_id": bot_id,
            "created_at": time.time(),
            "status": "success"
        }

    def post_comment(self, tweet_id: str, content: str, bot_id: str) -> Dict[str, Any]:
        """
        Публикация комментария к твиту

        Args:
            tweet_id (str): ID твита, к которому публикуется комментарий
            content (str): Содержание комментария
            bot_id (str): ID бота, от имени которого публикуется комментарий

        Returns:
            Dict[str, Any]: Ответ API с информацией о комментарии
        """
        self.logger.info(
            f"Бот {bot_id} комментирует твит {tweet_id}: {content[:50]}...")
        # Имитация задержки сети
        time.sleep(0.1)

        # Генерация ID комментария
        comment_id = f"comment_{uuid.uuid4().hex[:10]}"

        return {
            "id": comment_id,
            "tweet_id": tweet_id,
            "content": content,
            "bot_id": bot_id,
            "created_at": time.time(),
            "status": "success"
        }

    def post_reply(self, comment_id: str, content: str, bot_id: str) -> Dict[str, Any]:
        """
        Публикация ответа на комментарий

        Args:
            comment_id (str): ID комментария, на который публикуется ответ
            content (str): Содержание ответа
            bot_id (str): ID бота, от имени которого публикуется ответ

        Returns:
            Dict[str, Any]: Ответ API с информацией об ответе
        """
        self.logger.info(
            f"Бот {bot_id} отвечает на комментарий {comment_id}: {content[:50]}...")
        # Имитация задержки сети
        time.sleep(0.1)

        # Генерация ID ответа
        reply_id = f"reply_{uuid.uuid4().hex[:10]}"

        return {
            "id": reply_id,
            "comment_id": comment_id,
            "content": content,
            "bot_id": bot_id,
            "created_at": time.time(),
            "status": "success"
        }

    def like_tweet(self, tweet_id: str, bot_id: str) -> Dict[str, Any]:
        """
        Лайк твита

        Args:
            tweet_id (str): ID твита для лайка
            bot_id (str): ID бота, который ставит лайк

        Returns:
            Dict[str, Any]: Ответ API с информацией о действии
        """
        self.logger.info(f"Бот {bot_id} лайкает твит {tweet_id}")
        # Имитация задержки сети
        time.sleep(0.05)

        # Шанс ошибки 5%
        # if random.random() < 0.05:
        #     return {
        #         "status": "error",
        #         "message": "Rate limit exceeded"
        #     }

        return {
            "status": "success",
            "tweet_id": tweet_id,
            "bot_id": bot_id,
            "action": "like",
            "created_at": time.time()
        }

    def retweet(self, tweet_id: str, bot_id: str) -> Dict[str, Any]:
        """
        Ретвит

        Args:
            tweet_id (str): ID твита для ретвита
            bot_id (str): ID бота, который делает ретвит

        Returns:
            Dict[str, Any]: Ответ API с информацией о действии
        """
        self.logger.info(f"Бот {bot_id} ретвитит твит {tweet_id}")
        # Имитация задержки сети
        time.sleep(0.05)

        # Шанс ошибки 5%
        # if random.random() < 0.05:
        #     return {
        #         "status": "error",
        #         "message": "Rate limit exceeded"
        #     }

        # Генерация ID ретвита
        retweet_id = f"rt_{uuid.uuid4().hex[:10]}"

        return {
            "status": "success",
            "tweet_id": tweet_id,
            "retweet_id": retweet_id,
            "bot_id": bot_id,
            "action": "retweet",
            "created_at": time.time()
        }

    def view_tweet(self, tweet_id: str, bot_id: str) -> Dict[str, Any]:
        """
        Просмотр твита (для аналитики)

        Args:
            tweet_id (str): ID твита для просмотра
            bot_id (str): ID бота, который просматривает твит

        Returns:
            Dict[str, Any]: Ответ API с информацией о действии
        """
        self.logger.debug(f"Бот {bot_id} просматривает твит {tweet_id}")
        # Имитация задержки сети
        time.sleep(0.02)

        return {
            "status": "success",
            "tweet_id": tweet_id,
            "bot_id": bot_id,
            "action": "view",
            "created_at": time.time()
        }

    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Получение информации о твите

        Args:
            tweet_id (str): ID твита

        Returns:
            Dict[str, Any]: Информация о твите
        """
        self.logger.debug(f"Получение информации о твите {tweet_id}")
        # Имитация задержки сети
        time.sleep(0.1)

        return {
            "id": tweet_id,
            "content": f"Это мок-содержимое твита {tweet_id}",
            "author_id": f"author_{tweet_id[-5:]}",
            "created_at": time.time() - 3600,  # Час назад
            "like_count": random.randint(0, 100),
            "retweet_count": random.randint(0, 50),
            "reply_count": random.randint(0, 20)
        }

    def get_tweet_comments(self, tweet_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Получение комментариев к твиту

        Args:
            tweet_id (str): ID твита
            limit (int): Максимальное количество комментариев

        Returns:
            List[Dict[str, Any]]: Список комментариев
        """
        self.logger.debug(
            f"Получение комментариев к твиту {tweet_id}, лимит {limit}")
        # Имитация задержки сети
        time.sleep(0.2)

        # Генерация случайного количества комментариев
        num_comments = min(random.randint(0, 30), limit)

        comments = []
        for i in range(num_comments):
            comment_id = f"comment_{uuid.uuid4().hex[:10]}"
            bot_id = f"bot_{random.randint(1, 100)}"

            comments.append({
                "id": comment_id,
                "tweet_id": tweet_id,
                "content": f"Это мок-комментарий {i+1} к твиту {tweet_id}",
                "bot_id": bot_id,
                "created_at": time.time() - random.randint(0, 3600)
            })

        return comments


# Удобные функции для использования вне класса
def post_tweet(content: str, bot_id: str) -> Dict[str, Any]:
    """Обертка для TwitterClient.post_tweet"""
    client = TwitterClient()
    return client.post_tweet(content, bot_id)


def post_comment(tweet_id: str, content: str, bot_id: str) -> Dict[str, Any]:
    """Обертка для TwitterClient.post_comment"""
    client = TwitterClient()
    return client.post_comment(tweet_id, content, bot_id)


def post_reply(comment_id: str, content: str, bot_id: str) -> Dict[str, Any]:
    """Обертка для TwitterClient.post_reply"""
    client = TwitterClient()
    return client.post_reply(comment_id, content, bot_id)


def like_tweet(tweet_id: str, bot_id: str) -> Dict[str, Any]:
    """Обертка для TwitterClient.like_tweet"""
    client = TwitterClient()
    return client.like_tweet(tweet_id, bot_id)


def retweet(tweet_id: str, bot_id: str) -> Dict[str, Any]:
    """Обертка для TwitterClient.retweet"""
    client = TwitterClient()
    return client.retweet(tweet_id, bot_id)


def view_tweet(tweet_id: str, bot_id: str) -> Dict[str, Any]:
    """Обертка для TwitterClient.view_tweet"""
    client = TwitterClient()
    return client.view_tweet(tweet_id, bot_id)


def get_tweet(tweet_id: str) -> Dict[str, Any]:
    """Обертка для TwitterClient.get_tweet"""
    client = TwitterClient()
    return client.get_tweet(tweet_id)


def get_tweet_comments(tweet_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Обертка для TwitterClient.get_tweet_comments"""
    client = TwitterClient()
    return client.get_tweet_comments(tweet_id, limit)

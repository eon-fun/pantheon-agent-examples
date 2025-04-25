"""
Module with mock functions for working with the Twitter API.
This module simulates interaction with the Twitter API for testing.
"""
import time
import uuid
import random
import logging
from typing import Dict, Any, List, Optional


class TwitterClient:
    """
    Mock client for Twitter API
    """

    def __init__(self, use_real_api: bool = False):
        """
        Initialization of the Twitter client

        Args:
            use_real_api (bool): Flag for using the real API (not used in the current implementation)
        """
        self.logger = logging.getLogger("twitter_api")
        self.use_real_api = use_real_api
        self.logger.info("Initialization of Twitter client (mock)")

    def post_tweet(self, content: str, bot_id: str) -> Dict[str, Any]:
        """
        Publishes a tweet

        Args:
            content (str): Tweet content
            bot_id (str): Bot ID on whose behalf the tweet is published

        Returns:
            Dict[str, Any]: API response with tweet information
        """
        # Generate tweet ID
        tweet_id = f"tweet_{uuid.uuid4().hex[:10]}"

        return {
            "id": tweet_id,
            "content": content,
            "bot_id": bot_id,
            "created_at": time.time(),
            "status": "success"
        }

    def post_comment(self, action: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        Publishes a comment to a tweet

        Args:
            tweet_id (str): Tweet ID to which the comment is published
            content (str): Comment content
            bot_id (str): Bot ID on whose behalf the comment is published

        Returns:
            Dict[str, Any]: API response with comment information
        """
        # Generate comment ID
        comment_id = f"comment_{uuid.uuid4().hex[:10]}"
        action["content"] = content

        return {
            "action": action,
            "created_at": time.time(),
            "status": "success"
        }

    def post_reply(self, action: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        Publishes a reply to a comment

        Args:
            comment_id (str): Comment ID to which the reply is published
            content (str): Reply content
            bot_id (str): Bot ID on whose behalf the reply is published

        Returns:
            Dict[str, Any]: API response with reply information
        """
        # Generate reply ID
        reply_id = f"reply_{uuid.uuid4().hex[:10]}"

        return {
            "action": action,
            "created_at": time.time(),
            "status": "success"
        }

    def like_tweet(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Likes a tweet

        Args:
            tweet_id (str): Tweet ID for like
            bot_id (str): Bot ID that likes the tweet

        Returns:
            Dict[str, Any]: API response with action information
        """
        return {
            "status": "success",
            "action": action,
            "created_at": time.time()
        }

    def retweet(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retweets

        Args:
            tweet_id (str): Tweet ID to retweet
            bot_id (str): Bot ID who retweets

        Returns:
            Dict[str, Any]: API response with action information
        """
        # Generate retweet ID
        retweet_id = f"rt_{uuid.uuid4().hex[:10]}"

        return {
            "status": "success",
            "action": action,
            "created_at": time.time()
        }

    def view_tweet(self, tweet_id: str, bot_id: str) -> Dict[str, Any]:
        """
        Views a tweet (for analytics)

        Args:
            tweet_id (str): Tweet ID to view
            bot_id (str): Bot ID who views the tweet

        Returns:
            Dict[str, Any]: API response with action information
        """
        return {
            "status": "success",
            "tweet_id": tweet_id,
            "bot_id": bot_id,
            "action": "view",
            "created_at": time.time()
        }

    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Gets tweet information

        Args:
            tweet_id (str): Tweet ID

        Returns:
            Dict[str, Any]: Tweet information
        """

        return {
            "id": tweet_id,
            "content": f"This is mock content of tweet {tweet_id}",
            "author_id": f"author_{tweet_id[-5:]}",
            "created_at": time.time() - 3600,  # One hour ago
            "like_count": random.randint(0, 100),
            "retweet_count": random.randint(0, 50),
            "reply_count": random.randint(0, 20)
        }

    def get_tweet_comments(self, tweet_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Gets comments to a tweet

        Args:
            tweet_id (str): Tweet ID
            limit (int): Maximum number of comments

        Returns:
            List[Dict[str, Any]]: List of comments
        """
        # Generate a random number of comments
        num_comments = min(random.randint(0, 30), limit)

        comments = []
        for i in range(num_comments):
            comment_id = f"comment_{uuid.uuid4().hex[:10]}"
            bot_id = f"bot_{random.randint(1, 100)}"

            comments.append({
                "id": comment_id,
                "tweet_id": tweet_id,
                "content": f"This is mock comment {i+1} to tweet {tweet_id}",
                "bot_id": bot_id,
                "created_at": time.time() - random.randint(0, 3600)
            })

        return comments


# Convenient functions for use outside the class
def post_tweet(action: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for TwitterClient.post_tweet"""
    client = TwitterClient()
    return client.post_tweet(action["content"], action["bot_id"])


def post_comment(action: Dict[str, Any], content: str) -> Dict[str, Any]:
    """Wrapper for TwitterClient.post_comment"""
    client = TwitterClient()
    return client.post_comment(action, content)


def post_reply(action: Dict[str, Any], content: str) -> Dict[str, Any]:
    """Wrapper for TwitterClient.post_reply"""
    client = TwitterClient()
    return client.post_reply(action, content)


def like_tweet(action: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for TwitterClient.like_tweet"""
    client = TwitterClient()
    return client.like_tweet(action)


def retweet(action: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper for TwitterClient.retweet"""
    client = TwitterClient()
    return client.retweet(action)


def view_tweet(tweet_id: str, bot_id: str) -> Dict[str, Any]:
    """Wrapper for TwitterClient.view_tweet"""
    client = TwitterClient()
    return client.view_tweet(tweet_id, bot_id)


def get_tweet(tweet_id: str) -> Dict[str, Any]:
    """Wrapper for TwitterClient.get_tweet"""
    client = TwitterClient()
    return client.get_tweet(tweet_id)


def get_tweet_comments(tweet_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Wrapper for TwitterClient.get_tweet_comments"""
    client = TwitterClient()
    return client.get_tweet_comments(tweet_id, limit)

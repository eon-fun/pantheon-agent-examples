from DB.managers.tracked_accounts_manager import AlchemyTrackedAccountsManager
from DB.managers.user_manager import AlchemyUsersManager
from DB.sqlalchemy_database_manager import get_db
from config.config import config
from agents_tools_logger.main import log
from services.twitter.actions.follow import follow
from services.twitter.actions.get_likes_on_post import get_likes_on_post
from services.twitter.auth_client import TwitterAuthClient
from services.twitter.tweetscout_requests import fetch_user_tweets


async def process_follow_for_like():
    async for session in get_db():
        user_manager = AlchemyUsersManager(session)
        users = await user_manager.get_all_users()
        log.info(f"Received {len(users)} users")

        for user in users:
            log.info(f"Processing user {user.username}({user.id})")
            if user.followers_today >= config.MAX_FOLLOWERS_PER_DAY:
                log.info(f"User {user.username}({user.id}) has reached the limit of followers for today")
                continue

            username = user.username
            user_id = user.id
            tweets = (await fetch_user_tweets(username))
            log.info(f"Received {len(tweets)} tweets")
            limit_for_tweets = 10
            for tweet in tweets[:limit_for_tweets]:
                log.info(f"Processing tweet {tweet.id_str}")
                likes_data = await get_likes_on_post(
                    access_token=await TwitterAuthClient.get_access_token(str(user_id)),
                    tweet_id=tweet.id_str
                )
                likes_data = likes_data["data"]
                for like in likes_data:
                    log.info(f"Processing like {like['id']}")
                    try:
                        await follow(token=await TwitterAuthClient.get_access_token(str(user_id)),
                                     user_id=str(user_id),
                                     target_user_id=like["id"])
                        await user_manager.increment_followers(user_id)
                        tracked_account_manager = AlchemyTrackedAccountsManager(session)
                        await tracked_account_manager.add_tracked_account(user_id=user_id, account_id=like["id"])

                    except Exception as e:
                        log.warning(f"Failed to follow user {like['id']}: {e}")

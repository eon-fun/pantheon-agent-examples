from agents_tools_logger.main import log
from follow_unfollow_bot.config.config import config
from follow_unfollow_bot.DB.managers.tracked_accounts_manager import AlchemyTrackedAccountsManager
from follow_unfollow_bot.DB.managers.user_manager import AlchemyUsersManager
from follow_unfollow_bot.DB.sqlalchemy_database_manager import get_db
from follow_unfollow_bot_get_likes_on_post.main import get_likes_on_post
from tweetscout_utils.main import fetch_user_tweets
from twitter_ambassador_utils.main import TwitterAuthClient
from twitter_follow.main import follow


async def process_follow_for_like():
    async for session in get_db():
        user_manager = AlchemyUsersManager(session)
        users = await user_manager.get_all_users()
        log.info(f"Received {len(users)} users")

        for user in users:
            log.info(f"Processing user {user.username}({user.id})")
            if user.followers_today >= config.max_followers_per_day:
                log.info(f"User {user.username}({user.id}) has reached the limit of followers for today")
                continue

            username = user.username
            user_id = user.id
            tweets = await fetch_user_tweets(username)
            log.info(f"Received {len(tweets)} tweets")
            limit_for_tweets = 10
            for tweet in tweets[:limit_for_tweets]:
                log.info(f"Processing tweet {tweet.id_str}")
                likes_data = await get_likes_on_post(
                    access_token=await TwitterAuthClient.get_access_token(str(user_id)), tweet_id=tweet.id_str
                )
                likes_data = likes_data["data"]
                for like in likes_data:
                    log.info(f"Processing like {like['id']}")
                    try:
                        await follow(
                            token=await TwitterAuthClient.get_access_token(str(user_id)),
                            user_id=str(user_id),
                            target_user_id=like["id"],
                        )
                        await user_manager.increment_followers(user_id)
                        tracked_account_manager = AlchemyTrackedAccountsManager(session)
                        await tracked_account_manager.add_tracked_account(user_id=user_id, account_id=like["id"])

                    except Exception as e:
                        log.warning(f"Failed to follow user {like['id']}: {e}")

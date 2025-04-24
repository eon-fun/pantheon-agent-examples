from models.raid_state import RaidState
from constants import LIKE_PERCENTAGE, COMMENT_PERCENTAGE, REPLY_PERCENTAGE
import random
import logging


def plan_raid_actions(state: RaidState):
    """
    Plans actions for the raid

    Args:
        state (OrionState): Current state

    Returns:
        OrionState: Updated state
    """
    # Обновляем состояние
    # updated_state = state.copy()
    updated_state = {}
    assigned_bots = state["assigned_bots"]

    target_tweet_id = state["target_tweet_id"]

    # Создаем группы ботов для разных действий
    total_bots = len(assigned_bots)
    like_count = int(total_bots * LIKE_PERCENTAGE)
    comment_count = int(total_bots * COMMENT_PERCENTAGE)
    reply_count = total_bots - comment_count

    # Перемешиваем ботов для случайного распределения
    random.shuffle(assigned_bots)

    # Боты для лайков
    like_bots = random.sample(assigned_bots, like_count)
    for i, bot in enumerate(like_bots):
        delay = random.uniform(120, 600)  # 2-10 минут
        bot["actions"].append({
            "type": "like",
            "tweet_id": target_tweet_id,
            "delay": delay,
        })

    # Боты для комментариев
    comment_bots = random.sample(assigned_bots, comment_count)
    for i, bot in enumerate(comment_bots):
        delay = random.uniform(120, 600)  # 2-10 минут
        bot["actions"].append({
            "type": "comment",
            "tweet_id": target_tweet_id,
            "delay": delay,
            "status": "pending",
            "content": None
        })

    # Боты для ответов
    reply_bots = random.sample(assigned_bots, reply_count)
    for i, bot in enumerate(reply_bots):
        delay = random.uniform(120, 600)  # 2-10 минут
        bot["actions"].append({
            "type": "reply",
            "tweet_id": target_tweet_id,
            "delay": delay,
        })

    # Для ответов нужны комментарии, поэтому они будут добавлены позже

    # Отмечаем статус как ожидание генерации контента для первого действия
    updated_state["status"] = "generating_content"
    updated_state["messages"] = state["messages"]
    # Добавляем сообщение в лог
    updated_state["messages"].append({
        "type": "action_scheduling",
        "content": f"Scheduled raid actions: {like_count} likes, {comment_count} comments, {reply_count} replies"
    })

    print(
        f"Scheduled {like_count} likes, {comment_count} comments, {reply_count} replies")
    return updated_state


def action_scheduler(state: RaidState):
    """
    LangGraph node for action planning

    Args:
        state (OrionState): Current state

    Returns:
        OrionState: Updated state
    """
    return plan_raid_actions(state)

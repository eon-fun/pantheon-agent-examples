from models.raid_state import RaidState
from typing import List, Dict, Any
import random


# Bot roles
BOT_ROLES = [
    "seed",        # Инициатор обсуждения
    "advocate",    # Сторонник
    "skeptic",     # Скептик
    "expert",      # Эксперт
    "moderator",   # Модератор
    "enthusiast",  # Энтузиаст
    "newbie"       # Новичок
]

# Стили взаимодействия
ENGAGEMENT_STYLES = [
    "casual",      # Обычный пользователь
    "careful",     # Осторожный пользователь
    "enthusiast",  # Энтузиаст
    "lurker",      # Наблюдатель
    "strategic"    # Стратегический
]

# Матрица совместимости ролей (кто чаще всего взаимодействует с кем)
ROLE_COMPATIBILITY = {
    "seed": ["advocate", "skeptic", "newbie"],
    "advocate": ["skeptic", "expert", "enthusiast"],
    "skeptic": ["advocate", "expert", "moderator"],
    "expert": ["advocate", "skeptic", "newbie", "moderator"],
    "moderator": ["advocate", "skeptic", "expert"],
    "enthusiast": ["advocate", "newbie", "seed"],
    "newbie": ["expert", "advocate", "moderator"]
}


def get_available_bots(count: int) -> List[Dict[str, Any]]:
    """
    Returns a list of available bots

    Returns:
        List[Dict[str, Any]]: List of bots
    """
    # В реальном приложении здесь был бы запрос к БД или API
    # Here we create mock bots for testing

    # Создаем "count" ботов с разными ролями и стилями
    # Create "count" bots with different roles and styles
    bots = []
    for i in range(count):
        bot_id = f"bot_{i+1}"
        role = random.choice(BOT_ROLES)
        engagement_style = random.choice(ENGAGEMENT_STYLES)

        # Создаем персону бота
        bot = {
            "id": bot_id,
            "name": f"Bot {i+1}",
            "role": role,
            "engagement_style": engagement_style,
            "available": True,
        }

        bots.append(bot)

    return bots


def bot_registry(state: RaidState):
    """
    LangGraph node for bot management

    Args:
        state (OrionState): Current state

    Returns:
        RaidState: Updated state
    """
    # Determine the number of bots
    bot_count = state["bot_count"]

    # Select bots for the task
    selected_bots = get_available_bots(bot_count)

    # Update state depending on the task type
    # updated_state = state.copy()
    updated_state = {}

    # Add bots to the state
    updated_state["assigned_bots"] = []
    for bot in selected_bots:
        # Add bot with an empty action list
        updated_state["assigned_bots"].append({
            **bot,
            "actions": []
        })
    updated_state["messages"] = []
    # Add message to log
    updated_state["messages"].append({
        "type": "bot_assignment",
        "content": f"Selected {len(selected_bots)} bots for raid task"
    })

    updated_state["status"] = "pending"

    return updated_state

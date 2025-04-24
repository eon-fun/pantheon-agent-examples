from typing import TypedDict, List, Dict, Any, Optional


class RaidState(TypedDict):
    status: Optional[str]  # "pending", "active", "completed", "failed", "generating_content", "action_pending", "waiting"

    # Параметры задачи
    target_tweet_id: str
    topic: Optional[str] = "topic"
    bot_count: int

    # Состояние рейда
    assigned_bots: Optional[List[Dict[str, Any]]] = list()  # список ботов с заданиями
    executed_actions: Optional[List[Dict[str, Any]]] = list()  # выполненные действия

    # Метаданные
    messages: Optional[List[Dict[str, Any]]] = list()  # история сообщений/действий
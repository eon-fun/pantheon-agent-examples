from pydantic import BaseModel


class BaseConfigModel(BaseModel):
    """Базовая модель конфигурации."""

    class Config:
        from_attributes = True

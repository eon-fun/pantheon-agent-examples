from pydantic_settings import BaseSettings, SettingsConfigDict
from agents_tools_logger.main import log


class DBSettings(BaseSettings):
    user: str
    password: str = "postgres"
    host: str = "localhost"
    port: str = "5432"
    name: str = "postgres"

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(env_prefix="DB_")  # Автоматически подтягивает переменные с префиксом DB_


class FastAPISettings(BaseSettings):
    allowed_origins: list[str] = ["http://localhost:8080"]
    allowed_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    allowed_headers: list[str] = [
        "Access-Control-Allow-Headers",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
    ]
    allowed_credentials: bool = True


class Config(BaseSettings):
    app_title: str = "follow_unfollow_bot"
    app_description: str = "API for follow_unfollow_bot"
    app_version: str = "0.0.1"
    app_docs_url: str = "hidden"

    max_followers_per_day: int = 400

    db: DBSettings = DBSettings()
    fastapi: FastAPISettings = FastAPISettings()

    def check_configuration(self):
        if not self.db.user:
            log.warning("Environment variable DB_USER is not set!")


config = Config()
config.check_configuration()

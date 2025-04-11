from pydantic_settings import BaseSettings, SettingsConfigDict
from agents_tools_logger.main import log


class DBSettings(BaseSettings):
    user: str = "postgres"
    password: str = "password"
    host: str = "localhost"
    port: str = "5432"
    name: str = "new_solana_pairs"

    @property
    def url(self) -> str:
        connection_string = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        log.info(f"Connection string: {connection_string}")
        return connection_string

    model_config = SettingsConfigDict(env_prefix="DB_")


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


class DexToolsSettings(BaseSettings):
    api_key: str
    plan : str = "trial"
    rate_limit_by_second: int = 1

    class Config:
        env_prefix = "DEX_"  # Все переменные должны начинаться с DEX_
        env_file = ".env"  # Путь до .env файла (если нужен)

class BotSettings(BaseSettings):
    bot_token: str
    chat_id: int
    send_delay: int = 1
    max_length_message_for_photo: int = 1024

class Config(BaseSettings):
    app_title: str = "follow_unfollow_bot"
    app_description: str = "API for follow_unfollow_bot"
    app_version: str = "0.0.1"
    app_docs_url: str = "hidden"

    bot: BotSettings = BotSettings()
    db: DBSettings = DBSettings()
    fastapi: FastAPISettings = FastAPISettings()
    dex_tools: DexToolsSettings = DexToolsSettings()

    def check_configuration(self):
        if not self.db.user:
            log.warning("Environment variable DB_USER is not set!")


config = Config()
config.check_configuration()

from pydantic_settings import BaseSettings, SettingsConfigDict
from agents_tools_logger.main import log


class DBSettings(BaseSettings):
    user: str = "postgres"
    password: str = "Plaalen18"
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
    api_key: str = ""
    base_api_url: str = ""
    rate_limit_by_second: int = 1

class BotSettings(BaseSettings):
    bot_token: str ="5343231561:AAGHqNDPaW0AWFu1G86_d4SzklK6aZVzxPM"
    chat_id: int = -4777229652
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

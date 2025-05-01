from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from loguru import logger

class FastAPISettings(BaseSettings):
    allowed_origins: list[str] = Field(default=[
        "http://localhost:8080",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:1111",
    ])
    allowed_methods: list[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    allowed_headers: list[str] = Field(default=[
        "Access-Control-Allow-Headers",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
    ])
    allowed_credentials: bool = Field(default=True)


class DatabaseSettings(BaseSettings):
    db_user: str = Field(..., env="DB_USER", default="rag")
    db_password: str = Field(..., env="DB_PASSWORD", default="rag")
    db_host: str = Field(..., env="DB_HOST", default="localhost")
    db_port: str = Field(..., env="DB_PORT", default="5432")
    db_name: str = Field(..., env="DB_NAME", default="rag")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class AppConfig(BaseSettings):
    app_title: str = Field(default="Twitter Echo Bot")
    app_description: str = Field(default="API for Twitter Echo Bot")
    app_version: str = Field(default="0.0.1")
    app_docs_url: str = Field(default="hidden")
    fastapi: FastAPISettings = Field(default_factory=FastAPISettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)

    def check_configuration(self):
        required_vars = {
            "DB_USER": self.db.db_user,
            "DB_PASSWORD": self.db.db_password,
            "DB_HOST": self.db.db_host,
            "DB_PORT": self.db.db_port,
            "DB_NAME": self.db.db_name,
        }
        for var_name, var_value in required_vars.items():
            if not var_value:
                logger.warning(f"Environment variable {var_name} is not set!")


config = AppConfig()
config.check_configuration()

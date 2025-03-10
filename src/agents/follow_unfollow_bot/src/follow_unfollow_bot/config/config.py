from agents_tools_logger.main import log

from dotenv import load_dotenv
import os



load_dotenv()


class Config:
    APP_TITLE = "follow_unfollow_bot"
    APP_DESCRIPTION = "API for follow_unfollow_bot"
    APP_VERSION = "0.0.1"
    APP_DOCS_URL = "hidden"

    MAX_FOLLOWERS_PER_DAY = 400

    class DB:
        DB_USER = os.getenv("DB_USER", "")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "postgres")
        URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    class FASTAPI:
        ALLOWED_ORIGINS = [
            "http://localhost:8080",
        ]

        ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        ALLOWED_HEADERS = [
            "Access-Control-Allow-Headers",
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Origin",
        ]

        ALLOWED_CREDENTIALS = True


    @classmethod
    def check_configuration(cls):
        required_env_vars = {
            "DB_USER": cls.DB.DB_USER,

        }
        for var_name, var_value in required_env_vars.items():
            if not var_value or var_value == "":
                log.warning(f"Environment variable {var_name} is not set!")


config = Config()
config.check_configuration()

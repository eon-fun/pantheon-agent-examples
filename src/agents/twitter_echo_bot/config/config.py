from custom_logs.custom_logs import log
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_TITLE = "Twitter Echo Bot"
    APP_DESCRIPTION = "API for Twitter Echo Bot"
    APP_VERSION = "0.0.1"
    APP_DOCS_URL = "hidden"

    class FASTAPI:
        ALLOWED_ORIGINS = [
            "http://localhost:8080",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:1111",

        ]

        ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        ALLOWED_HEADERS = [
            "Access-Control-Allow-Headers",
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Origin",
        ]

        ALLOWED_CREDENTIALS = True
    class DB:
        DB_USER = os.getenv("DB_USER", )
        DB_PASSWORD = os.getenv("DB_PASSWORD", )
        DB_HOST = os.getenv("DB_HOST", )
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME", )



    @classmethod
    def check_configuration(cls):
        required_env_vars = {
            "DB_USER": cls.DB.DB_USER,
            "DB_PASSWORD": cls.DB.DB_PASSWORD,
            "DB_HOST": cls.DB.DB_HOST,
            "DB_PORT": cls.DB.DB_PORT,
            "DB_NAME": cls.DB.DB_NAME,
        }
        for var_name, var_value in required_env_vars.items():
            if not var_value or var_value == "":
                log.warning(f"Environment variable {var_name} is not set!")


config = Config()
config.check_configuration()

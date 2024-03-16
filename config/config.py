from os import getenv
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:
    TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
    POSTGRES_CONN: str = getenv("POSTGRES_CONN")
    POSTGRES_JDBC_URL: str = getenv("POSTGRES_JDBC_URL")
    POSTGRES_USERNAME: str = getenv("POSTGRES_USERNAME")
    POSTGRES_PASSWORD: str = getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = getenv("POSTGRES_PORT")
    POSTGRES_DATABASE: str = getenv("POSTGRES_DATABASE")


class Constants:
    TRANSPORTS = {"Пешком": 20, "Автомобиль": 80, "Самолёт": 900, "Иное": 40}
    TIME_PATTERN = "%d/%m/%Y %H:%M"


@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_constants():
    return Constants()

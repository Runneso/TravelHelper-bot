from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    TELEGRAM_TOKEN: SecretStr

    TOM_TOM_APIKEY: SecretStr
    OPEN_WEATHER_APIKEY: SecretStr

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DATABASE: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class Constants:
    TRANSPORTS = {"Пешком": 20, "Автомобиль": 80, "Самолёт": 900, "Иное": 40}  # км/ч
    TIME_PATTERN = "%d/%m/%Y %H:%M"


@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_constants():
    return Constants()

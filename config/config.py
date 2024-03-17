from os import getenv
from functools import lru_cache
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class Settings:
    TELEGRAM_TOKEN: str = getenv("TELEGRAM_TOKEN")
    TOM_TOM_APIKEY: str = getenv("TOM_TOM_APIKEY")
    OPEN_WEATHER_APIKEY: str = getenv("OPEN_WEATHER_APIKEY")
    POSTGRES_CONN: str = getenv("POSTGRES_CONN")
    POSTGRES_JDBC_URL: str = getenv("POSTGRES_JDBC_URL")
    POSTGRES_USERNAME: str = getenv("POSTGRES_USERNAME")
    POSTGRES_PASSWORD: str = getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST: str = getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = getenv("POSTGRES_PORT")
    POSTGRES_DATABASE: str = getenv("POSTGRES_DATABASE")


class Constants:
    TRANSPORTS = {"Пешком": 20, "Автомобиль": 80, "Самолёт": 900, "Иное": 40}  # км/ч
    TIME_PATTERN = "%d/%m/%Y %H:%M"
    six_hour_am = datetime.strptime("6:00", "%H:%M").time()
    eight_hour_pm = datetime.strptime("20:00", "%H:%M").time()



@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_constants():
    return Constants()

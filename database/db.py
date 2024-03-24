from config import config

from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass


settings: config.Settings = config.get_settings()
database_url = f"postgresql+psycopg2://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD.get_secret_value()}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}"
engine = create_engine(database_url)


def get_session_maker() -> sessionmaker[Session]:
    session_maker = sessionmaker(bind=engine)
    return session_maker

import datetime
from typing import List
from .db import Base, engine
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, Integer, Boolean, Float, JSON, Date
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    login: Mapped[str] = mapped_column(Text, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(Text, nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)


class Journeys(Base):
    __tablename__ = "journeys"

    journey_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journey_name: Mapped[str] = mapped_column(Text, nullable=False)
    journey_author: Mapped[str] = mapped_column(Text, nullable=False)
    transport_type: Mapped[str] = mapped_column(Text, nullable=False)
    journey_length: Mapped[int] = mapped_column(Integer, nullable=False)
    journey_path: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    journey_delays: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=False)
    datetime_start: Mapped[datetime]
    journey_participants: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)


def create_db() -> None:
    Base.metadata.create_all(engine)

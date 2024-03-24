from .db import Base, engine

from typing import List
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, Integer, Float, Boolean, Date
from sqlalchemy.dialects.postgresql import ARRAY
from pydantic import BaseModel


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    username: Mapped[str] = mapped_column(Text, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    biography: Mapped[str] = mapped_column(Text, nullable=True)


class Journeys(Base):
    __tablename__ = "journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    transport_type: Mapped[str] = mapped_column(Text, nullable=False)
    datetime_start: Mapped[datetime]
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    path: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    lat: Mapped[List[float]] = mapped_column(ARRAY(Float), nullable=False)
    lon: Mapped[List[float]] = mapped_column(ARRAY(Float), nullable=False)
    time_in_path: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=False)
    delays: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=False)
    participants: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)


class InviteTokens(Base):
    __tablename__ = "invite_tokens"

    code: Mapped[str] = mapped_column(Text, primary_key=True)
    journey_id: Mapped[str] = mapped_column(Text, nullable=False)


class Notes(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    isPublic: Mapped[bool] = mapped_column(Boolean, nullable=False)
    journey_id: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False, default=datetime.now())


class AddNode(BaseModel):
    name: str
    lat: float
    lon: float
    time_in_path: int
    delay: int


def create_db() -> None:
    Base.metadata.create_all(engine)

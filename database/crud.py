from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select
from .models import *


class CRUD:
    def get_user_by_id(self, sessionmaker: sessionmaker[Session], user_id: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Users).filter(Users.user_id == user_id)
                result = session.execute(sql_query).scalars().first()
                session.close()
                return result

    def create_user(self, sessionmaker: sessionmaker[Session], user_data: Users):
        with sessionmaker() as session:
            with session.begin():
                session.add(user_data)
                session.commit()
                session.close()

    def create_journey(self, sessionmaker: sessionmaker[Session], journey_data: Journeys):
        with sessionmaker() as session:
            with session.begin():
                session.add(journey_data)
                session.commit()
                session.close()

    def get_my_journeys(self, sessionmaker: sessionmaker[Session], user_id: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.journey_participants.contains([user_id]))
                result = session.execute(sql_query).scalars().all()
                session.close()
                return result


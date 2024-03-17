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
                sql_query = select(Journeys).filter(Journeys.journey_participants.contains([user_id])).order_by(
                    Journeys.journey_id)
                result = session.execute(sql_query).scalars().all()
                session.close()
                return result

    def get_journey_by_id(self, sessionmaker: sessionmaker[Session], journey_id: int):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.journey_id == journey_id)
                result = session.execute(sql_query).scalars().first()
                session.close()
                return result

    def add_friend_in_journey(self, sessionmaker: sessionmaker[Session], friend_id: str, journey_id: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.journey_id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                journey.journey_participants = list(journey.journey_participants) + [friend_id]
                session.commit()
                session.close()

    def remove_friend_from_journey(self, sessionmaker: sessionmaker[Session], friend_id: str, journey_id: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.journey_id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                journey.journey_participants = list(journey.journey_participants)
                journey.journey_participants.remove(friend_id)
                session.commit()
                session.close()

    def remove_journey(self, sessionmaker: sessionmaker[Session], journey_data: Journeys):
        with sessionmaker() as session:
            with session.begin():
                session.delete(journey_data)
                session.commit()
                session.close()

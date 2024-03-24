from .models import Journeys, Users, Notes, InviteTokens, AddNode
from config import Constants, get_constants
from services import GeoPyAPI

from datetime import datetime
from math import ceil

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select

geo_py_API: GeoPyAPI = GeoPyAPI()
constants: Constants = get_constants()


class CRUD:
    def get_user_by_id(self, sessionmaker: sessionmaker[Session], user_id: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Users).filter(Users.user_id == user_id)
                result = session.execute(sql_query).scalars().first()
                session.close()
                return result

    def get_notes_by_type_and_journey_id(self, sessionmaker: sessionmaker[Session], journey_id: str, note_type: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Notes).filter(Notes.note_type.like(note_type), Notes.journey_id.like(journey_id))
                result = session.execute(sql_query).scalars().all()
                session.close()
                return result

    def get_token_by_value(self, sessionmaker: sessionmaker[Session], code: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(InviteTokens).filter(InviteTokens.code == code)
                result = session.execute(sql_query).scalars().first()
                session.close()
                return result

    def get_my_journeys(self, sessionmaker: sessionmaker[Session], user_id: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.participants.contains([user_id])).order_by(
                    Journeys.id)
                result = session.execute(sql_query).scalars().all()
                session.close()
                return result

    def get_journey_by_id(self, sessionmaker: sessionmaker[Session], journey_id: int):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.id == journey_id)
                result = session.execute(sql_query).scalars().first()
                session.close()
                return result

    def create_user(self, sessionmaker: sessionmaker[Session], user_data: Users):
        with sessionmaker() as session:
            with session.begin():
                session.add(user_data)
                session.commit()
                session.close()

    def create_note(self, sessionmaker: sessionmaker[Session], note_data: Notes):
        with sessionmaker() as session:
            with session.begin():
                session.add(note_data)
                session.commit()
                session.close()

    def create_token(self, sessionmaker: sessionmaker[Session], token_data: InviteTokens):
        with sessionmaker() as session:
            with session.begin():
                session.add(token_data)
                session.commit()
                session.close()

    def create_journey(self, sessionmaker: sessionmaker[Session], journey_data: Journeys):
        with sessionmaker() as session:
            with session.begin():
                session.add(journey_data)
                session.commit()
                session.close()

    def create_new_node(self, sessionmaker: sessionmaker[Session], journey_id: str, node: AddNode):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                journey.lat = list(journey.lat) + [node.lat]
                journey.lon = list(journey.lon) + [node.lon]
                journey.path = list(journey.path) + [node.name]
                journey.time_in_path = list(journey.time_in_path) + [node.time_in_path]
                journey.delays = list(journey.delays) + [node.delay]
                session.commit()
                session.close()

    def add_friend_in_journey(self, sessionmaker: sessionmaker[Session], friend_id: str, journey_id: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                journey.participants = list(journey.participants) + [friend_id]
                session.commit()
                session.close()

    def remove_friend_from_journey(self, sessionmaker: sessionmaker[Session], friend_id: str, journey_id: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                journey.participants = list(journey.participants)
                journey.participants.remove(friend_id)
                session.commit()
                session.close()

    def remove_note(self, sessionmaker: sessionmaker[Session], note_data: Notes):
        with sessionmaker() as session:
            with session.begin():
                session.delete(note_data)
                session.commit()
                session.close()

    def remove_token(self, sessionmaker: sessionmaker[Session], token_data: InviteTokens):
        with sessionmaker() as session:
            with session.begin():
                session.delete(token_data)
                session.commit()
                session.close()

    def remove_journey(self, sessionmaker: sessionmaker[Session], journey_data: Journeys):
        with sessionmaker() as session:
            with session.begin():
                session.delete(journey_data)
                session.commit()
                session.close()

    def change_age(self, sessionmaker: sessionmaker[Session], user_id: str, new_age: int):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Users).filter(Users.user_id == user_id)
                user = session.execute(sql_query).scalars().first()
                user.age = new_age
                session.commit()
                session.close()

    def change_biography(self, sessionmaker: sessionmaker[Session], user_id: str, new_biography: int):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Users).filter(Users.user_id == user_id)
                user = session.execute(sql_query).scalars().first()
                user.biography = new_biography
                session.commit()
                session.close()

    def change_location(self, sessionmaker: sessionmaker[Session], user_id: str, lat: float, lon: float, location: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Users).filter(Users.user_id == user_id)
                user = session.execute(sql_query).scalars().first()
                user.lat = lat
                user.lon = lon
                user.location = location
                session.commit()
                session.close()

    def change_journey_name(self, sessionmaker: sessionmaker[Session], journey_id: int, new_name: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                journey.name = new_name
                session.commit()
                session.close()

    def change_journey_transport_type(self, sessionmaker: sessionmaker[Session], journey_id: int,
                                      new_transport_type: str):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                journey.transport_type = new_transport_type
                session.commit()
                session.close()

    def change_journey_datetime_start(self, sessionmaker: sessionmaker[Session], journey_id: int,
                                      new_datetime_start: datetime):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                journey.datetime_start = new_datetime_start
                session.commit()
                session.close()

    async def recalculate_time_in_path(self, sessionmaker: sessionmaker[Session], journey_id: int):
        with sessionmaker() as session:
            with session.begin():
                sql_query = select(Journeys).filter(Journeys.id == journey_id)
                journey = session.execute(sql_query).scalars().first()
                transport_type = journey.transport_type
                lat, lon = journey.lat, journey.lon
                new_time_in_path = list()
                for index in range(1, len(lat)):
                    coordinates1 = (lat[index-1], lon[index-1])
                    coordinates2 = (lat[index], lon[index])
                    distance = await geo_py_API.get_distance(coordinates1, coordinates2)
                    new_time_in_path.append(ceil(distance / constants.TRANSPORTS[transport_type]))
                journey.time_in_path = new_time_in_path
                session.commit()
                session.close()

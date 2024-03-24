from services import GeoPyAPI
from states import CreateJourneyHandler
from keyboards import create_journey_handler_keyboard
from database import CRUD, Journeys
from config import get_settings, Settings, get_constants, Constants
from lexicon import create_journey_handler_lexicon

from datetime import datetime
from math import ceil

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter, Command
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

geo_py_API: GeoPyAPI = GeoPyAPI()

lexicon = create_journey_handler_lexicon
keyboard = create_journey_handler_keyboard

create_journey: Router = Router()
db: CRUD = CRUD()

settings: Settings = get_settings()
constants: Constants = get_constants()


def get_user_data(message: Message) -> dict[str]:
    """

    :param message:
    :return:
    """
    data = dict()
    data["user_id"]: str = str(message.from_user.id)
    data["username"] = message.from_user.username
    data["first_name"] = message.from_user.first_name
    data["last_name"] = message.from_user.last_name
    data["text"] = message.text
    return data


@create_journey.message(Command(commands=["create_journey"]), StateFilter(default_state))
async def create_journey_command(message: Message, state: FSMContext):
    """
    Хэндлер для команды.
    :param message:
    :param state:
    """
    await message.answer(lexicon.start_creation)
    await state.set_state(CreateJourneyHandler.name)


@create_journey.message(StateFilter(CreateJourneyHandler.name))
async def get_name(message: Message, state: FSMContext):
    """
    Хэндлер для получения имени.
    :param message:
    :param state:
    """
    user_data = get_user_data(message)
    name = user_data["text"]
    await message.answer(lexicon.transport_string, reply_markup=keyboard.kb_transport_type)
    await state.update_data(name=name)
    await state.set_state(CreateJourneyHandler.transport_type)


@create_journey.message(StateFilter(CreateJourneyHandler.transport_type))
async def get_transport_type(message: Message, state: FSMContext):
    """
    Хэндлер для получения типа транспорта.
    :param message:
    :param state:
    """
    user_data = get_user_data(message)
    transport_type = user_data["text"]
    if transport_type not in constants.TRANSPORTS.keys():
        await message.answer(lexicon.Errors.invalid_transport_type)
    else:
        await message.answer(lexicon.start_datetime)
        await state.update_data(transport_type=transport_type)
        await state.set_state(CreateJourneyHandler.datetime_start)


@create_journey.message(StateFilter(CreateJourneyHandler.datetime_start))
async def get_datetime_start(message: Message, state: FSMContext):
    """
    Хэндлер для получения даты начала.
    :param message:
    :param state:
    """
    user_data = get_user_data(message)
    datetime_start = user_data["text"]
    try:
        datetime_start = datetime.strptime(datetime_start, constants.TIME_PATTERN)
    except Exception as error:
        await message.answer(lexicon.Errors.invalid_datetime_start)
        logger.error(error)
    else:
        await message.answer(lexicon.length_string)
        await state.update_data(datetime_start=datetime_start)
        await state.set_state(CreateJourneyHandler.length)


@create_journey.message(StateFilter(CreateJourneyHandler.length))
async def get_length(message: Message, state: FSMContext,
                     sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения длины поездки.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    length = user_data["text"]
    user = db.get_user_by_id(sessionmaker, user_data["user_id"])
    try:
        length = int(length)
        if not (1 <= length <= 30):
            raise ValueError
    except Exception as error:
        await message.answer(lexicon.Errors.invalid_length)
        logger.error(error)
    else:
        await message.answer(lexicon.node_name_string)
        await state.update_data(array_node_names=[user.location])
        await state.update_data(array_lat=[user.lat])
        await state.update_data(array_lon=[user.lon])
        await state.update_data(length=length)
        await state.set_state(CreateJourneyHandler.node_name)


@create_journey.message(StateFilter(CreateJourneyHandler.node_name))
async def get_node_name(message: Message, state: FSMContext):
    """
    Хэндлер для получения название пункта.
    :param message:
    :param state:
    """
    user_data = get_user_data(message)
    node_name = user_data["text"]
    location = await geo_py_API.get_coordinates(node_name)
    if location is None:
        await message.answer(lexicon.Errors.invalid_node_name)
    else:
        data = await state.get_data()
        lat, lon = location
        array_node_names = data.get("array_node_names", list()) + [node_name]
        array_lat = data.get("array_lat", list()) + [lat]
        array_lon = data.get("array_lon", list()) + [lon]
        array_time_in_path = data.get("array_time_in_path", list())

        if len(array_lat) > 1:
            coordinates_1 = array_lat[-2], array_lon[-2]
            coordinates_2 = array_lat[-1], array_lon[-1]
            distance = await geo_py_API.get_distance(coordinates_1, coordinates_2)
            time = ceil(distance / constants.TRANSPORTS[data["transport_type"]] / 24)
            array_time_in_path.append(time)

        await message.answer(lexicon.delay(node_name))
        await state.update_data(array_node_names=array_node_names)
        await state.update_data(array_lat=array_lat)
        await state.update_data(array_lon=array_lon)
        await state.update_data(array_time_in_path=array_time_in_path)
        await state.set_state(CreateJourneyHandler.node_delay)


@create_journey.message(StateFilter(CreateJourneyHandler.node_delay))
async def get_node_delay(message: Message, state: FSMContext,
                         sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения времени прибывания на пункте.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    node_delay = user_data["text"]
    try:
        node_delay = int(node_delay)
    except Exception as error:
        await message.answer(lexicon.Errors.invalid_node_delay)
        logger.error(error)
    else:
        data = await state.get_data()
        length = data["length"]
        array_node_delays = data.get("array_node_delays", list()) + [node_delay]
        if len(array_node_delays) == length:
            journey = Journeys(name=data["name"], author=message.from_user.id, transport_type=data["transport_type"],
                               datetime_start=data["datetime_start"], length=data["length"],
                               path=data["array_node_names"], time_in_path=data["array_time_in_path"],
                               lat=data["array_lat"], lon=data["array_lon"], delays=array_node_delays,
                               participants=[user_data["user_id"]])
            db.create_journey(sessionmaker, journey)
            await message.answer(lexicon.end_creation)
            await state.clear()
        else:
            await message.answer(lexicon.node_name_string)
            await state.update_data(array_node_delays=array_node_delays)
            await state.set_state(CreateJourneyHandler.node_name)

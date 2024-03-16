from datetime import datetime, timedelta
from math import ceil

from aiogram import Router
from aiogram.types import *
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from sqlalchemy.orm import sessionmaker, Session

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from loguru import logger

from database import CRUD, Users, Journeys
from strings import *
from states import FSMStart, FSMCreateJourney, FSMMyJourneys
from keyboards import keyboard_location, keyboard_transport_type, keyboard_switch
from config import get_constants

locator = Nominatim(user_agent="GetLoc")
router: Router = Router()
db = CRUD()
constants = get_constants()


def get_repr_date(date: datetime):
    return datetime.strftime(date, constants.TIME_PATTERN)


def clc_delta(node1: str, node2: str, transport_type: str) -> float:
    location1, location2 = locator.geocode(node1), locator.geocode(node2)
    coordinates1 = (location1.latitude, location1.longitude)
    coordinates2 = (location2.latitude, location2.longitude)
    print(coordinates1, coordinates2)
    distance = geodesic(coordinates1, coordinates2).kilometers
    return ceil(distance / constants.TRANSPORTS[transport_type])


def clc_nodes(node_data: Journeys, sessionmaker: sessionmaker[Session]) -> str:
    user = db.get_user_by_id(sessionmaker, node_data.journey_author)
    curr_time = node_data.datetime_start
    result = [f"Выезд - {user.city}, {user.country}: {get_repr_date(curr_time)}"]
    delays = list(node_data.journey_delays)
    path = [f"{user.city, user.country}"] + list(node_data.journey_path)
    for index in range(1, len(path)):
        node1, node2 = path[index - 1], path[index]
        delta = clc_delta(node1, node2, node_data.transport_type)
        curr_time += timedelta(hours=delta)
        result.append(
            f"{path[index]}: с {get_repr_date(curr_time)} до {get_repr_date(curr_time + timedelta(days=delays[index - 1]))}")
        curr_time += timedelta(days=delays[index - 1])
    return f"\n{down}\n".join(result)


def get_data(node_data: Journeys, sessionmaker: sessionmaker[Session]) -> str:
    answer = (f"ID: {node_data.journey_id}\n"
              f"Название: {node_data.journey_name}\n"
              f"Тип транспорта: {node_data.transport_type}\n"
              f"Участники путешествия: {', '.join([db.get_user_by_id(sessionmaker, user_id).login + f' (ID: {user_id})' for user_id in node_data.journey_participants])}\n")
    nodes = clc_nodes(node_data, sessionmaker)
    return answer + "\n" + nodes


@router.message(CommandStart(), StateFilter(default_state))
async def start_command(message: Message, state: FSMContext,
                        sessionmaker: sessionmaker[Session]):
    user_id = message.from_user.id
    username = message.from_user.username
    already = db.get_user_by_id(sessionmaker, str(user_id))
    if already:
        await message.answer(hello("@" + username))
    else:
        await message.answer(hello_new_user("@" + username))
        await state.set_state(FSMStart.get_age)


@router.message(Command(commands=["help"]), StateFilter(default_state))
async def help_command(message: Message, state: FSMContext):
    await message.answer(help_string)


@router.message(Command(commands=["profile"]), StateFilter(default_state))
async def profile_command(message: Message, state: FSMContext,
                          sessionmaker: sessionmaker[Session]):
    user_id = message.from_user.id
    user = db.get_user_by_id(sessionmaker, str(user_id))
    await message.answer(f"ID: {message.from_user.id},\n"
                         f"Никнейм: {message.from_user.username},\n"
                         f"Возраст: {user.age},\n"
                         f"Страна: {user.country},\n"
                         f"Город: {user.city},\n"
                         f"Биография: {user.bio}."
                         )


@router.message(Command(commands=["create_journey"]), StateFilter(default_state))
async def create_journey_command(message: Message, state: FSMContext):
    await message.answer("Вижу ты решил отправиться в путешествие. Круто! Укажи название путешествия.")
    await state.set_state(FSMCreateJourney.get_name)


@router.message(Command(commands=["my_journeys"]), StateFilter(default_state))
async def my_journeys(message: Message, state: FSMContext,
                      sessionmaker: sessionmaker[Session]):
    user_id = message.from_user.id
    journeys = db.get_my_journeys(sessionmaker, str(user_id))
    if journeys:
        await state.update_data(index=0)
        await message.answer(get_data(journeys[0], sessionmaker), reply_markup=keyboard_switch)
        await state.set_state(FSMMyJourneys.my_journeys)
    else:
        await message.answer("У вас нет активных путешествий.")


@router.callback_query(StateFilter(FSMMyJourneys.my_journeys))
async def FSMMyJourneys1(callback: CallbackQuery, state: FSMContext,
                         sessionmaker: sessionmaker[Session]):
    user_id = callback.from_user.id
    journeys = db.get_my_journeys(sessionmaker, str(user_id))
    n = len(journeys)
    if callback.data == "left":
        index = (await state.get_data())["index"]
        if index == 0:
            await callback.answer("Это самое первое путешествие!")
        else:
            text = get_data(journeys[index - 1], sessionmaker)
            await state.update_data(index=(index - 1))
            await callback.message.edit_text(text, reply_markup=keyboard_switch)
        await state.set_state(FSMMyJourneys.my_journeys)
    elif callback.data == "right":
        index = (await state.get_data())["index"]
        if index == n - 1:
            await callback.answer("Это самое последнее путешествие!")
        else:
            text = get_data(journeys[index + 1], sessionmaker)
            await state.update_data(index=(index + 1))
            await callback.message.edit_text(text, reply_markup=keyboard_switch)
        await state.set_state(FSMMyJourneys.my_journeys)
    else:
        await callback.message.delete()
        await state.clear()


@router.message(StateFilter(FSMCreateJourney.get_name))
async def FSMCreateJourney1(message: Message, state: FSMContext):
    await state.update_data(journey_name=message.text)
    await message.answer("Теперь укажи тип транспорта.", reply_markup=keyboard_transport_type)
    await state.set_state(FSMCreateJourney.get_transport_type)


@router.message(StateFilter(FSMCreateJourney.get_transport_type))
async def FSMCreateJourney2(message: Message, state: FSMContext):
    if message.text not in constants.TRANSPORTS.keys():
        await message.answer("Укажи верный тип транспорта, используя кнопки.", reply_markup=keyboard_transport_type)
        await state.set_state(FSMCreateJourney.get_transport_type)
    else:
        await state.update_data(journey_transport_type=message.text)
        await message.answer(
            "Теперь укажи дату начала поездки в формате {день}/{месяц}/{год} {часы}:{минуты}.\n"
            "Например 10/10/2021 13:15")
        await state.set_state(FSMCreateJourney.get_datetime_start)


@router.message(StateFilter(FSMCreateJourney.get_datetime_start))
async def FSMCreateJourney3(message: Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, constants.TIME_PATTERN)
    except ValueError as error:
        await message.answer("Укажи верную даты в формате {день}/{месяц}/{год} {часы}:{минуты}.")
        await state.set_state(FSMCreateJourney.get_datetime_start)
        logger.error(error)
    else:
        await state.update_data(journey_datetime_start=date)
        await message.answer("Со временем определились, теперь время определится с длинной поездки.\n"
                             "Сколько пунктов ты хочешь в процессе путешествия?")
        await state.set_state(FSMCreateJourney.get_journey_length)


@router.message(StateFilter(FSMCreateJourney.get_journey_length))
async def FSMCreateJourney4(message: Message, state: FSMContext):
    try:
        n = int(message.text)
    except ValueError as error:
        await message.answer("Отправь верное количество пунктов.")
        await state.set_state(FSMCreateJourney.get_journey_length)
        logger.error(error)
    else:
        await state.update_data(journey_length=n)
        await message.answer("Теперь введи название пункта в формате {название}, {город}, {страна}.\n"
                             "Например: Малиновка, Калининград, Россия")
        await state.set_state(FSMCreateJourney.get_node_name)


@router.message(StateFilter(FSMCreateJourney.get_node_name))
async def FSMCreateJourney5(message: Message, state: FSMContext):
    find = locator.geocode(message.text)
    if find is None:
        await message.answer("Данная локация не найдена.")
        await state.set_state(FSMCreateJourney.get_node_name)
    else:
        path = (await state.get_data()).get("path", [])
        path.append(message.text)
        await state.update_data(path=path)
        await message.answer(f"Теперь введи количество дней, которые ты хочешь провести в {message.text}.")
        await state.set_state(FSMCreateJourney.get_node_delay)


@router.message(StateFilter(FSMCreateJourney.get_node_delay))
async def FSMCreateJourney6(message: Message, state: FSMContext, sessionmaker: sessionmaker[Session]):
    try:
        delay = int(message.text)
    except ValueError as error:
        await message.answer("Отправь верное количество пунктов.")
        await state.set_state(FSMCreateJourney.get_node_delay)
        logger.error(error)
    else:
        data = await state.get_data()
        delays = data.get("delays", [])
        delays.append(delay)
        await state.update_data(delays=delays)
        if len(delays) == data["journey_length"]:
            data = await state.get_data()
            journey = Journeys(journey_name=data["journey_name"], journey_author=str(message.from_user.id),
                               transport_type=data["journey_transport_type"], journey_length=data["journey_length"],
                               journey_path=data["path"], journey_delays=data["delays"],
                               datetime_start=data["journey_datetime_start"],
                               journey_participants=[str(message.from_user.id)]
                               )
            db.create_journey(sessionmaker, journey)
            await message.answer(
                "Путешествие успешно добавлено, чтобы посмотреть свои путешествия используй команду /my_journeys.\n\n"
                "Чтобы получить доступ к определённому путешествию по ID, используй /journey {ID}.\n\n"
                "Если захочешь удалить или изменить данные о поездки, используй /delete_journey {ID} и "
                "/update_journey {ID} соответственно.\n\n"
                "Чтобы добавить или удалить друга с ID1 в путешествие ID2, используй /append_friend {ID1} {ID2} и "
                "/delete_friend {ID1} {ID2} соотвественно.")
            await state.clear()
        else:
            await message.answer("Теперь введи название пункта в формате {название}, {город}, {страна}.\n"
                                 "Например: Малиновка, Калининград, Россия")
            await state.set_state(FSMCreateJourney.get_node_name)


@router.message(StateFilter(FSMStart.get_age))
async def FSMStart1(message: Message, state: FSMContext):
    try:
        age = int(message.text)
    except ValueError as error:
        await message.answer("Отправь нам верный возвраст.")
        await state.set_state(FSMStart.get_age)
        logger.error(error)
    else:
        await state.update_data(age=age)
        await message.answer(location_string, reply_markup=keyboard_location)
        await state.set_state(FSMStart.get_location)


@router.message(StateFilter(FSMStart.get_location))
async def FSMStart2(message: Message, state: FSMContext):
    try:
        latitude = message.location.latitude
        longitude = message.location.longitude
        result = locator.reverse(f"{latitude}, {longitude}")
        result = str(result).split(", ")
        await state.update_data(country=result[-1])
        await state.update_data(city=result[4])
    except AttributeError as error:
        logger.error(error)
        await message.answer("Отправь нам верную геопозицию.")
        await state.set_state(FSMStart.get_location)
    else:
        await message.answer(bio_string)
        await state.set_state(FSMStart.get_bio)


@router.message(StateFilter(FSMStart.get_bio))
async def FSMStart3(message: Message, state: FSMContext,
                    sessionmaker: sessionmaker[Session]):
    await state.update_data(bio=message.text)
    data = await state.get_data()
    user = Users(user_id=message.from_user.id, login=message.from_user.username,
                 age=data["age"], country=data["country"], city=data["city"], bio=data["bio"])
    db.create_user(sessionmaker, user)
    await message.answer(info_string)
    await state.clear()

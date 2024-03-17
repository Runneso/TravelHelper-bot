from datetime import datetime, timedelta
from math import ceil
from typing import List, Tuple

from PIL import Image
from io import BytesIO

from aiogram import Router
from aiogram.types import *
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from sqlalchemy.orm import sessionmaker, Session

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from loguru import logger
from staticmap import StaticMap, Line, CircleMarker

from database import CRUD, Users, Journeys
from services import TomTomAPI, OpenWeatherAPI
from strings import *
from states import FSMStart, FSMCreateJourney, FSMMyJourneys
from keyboards import keyboard_location, keyboard_transport_type, keyboard_switch, keyboard_resolution
from config import get_constants, Constants, get_settings, Settings

locator: Nominatim = Nominatim(user_agent="GetLoc")
tom_tom_API: TomTomAPI = TomTomAPI()
open_weather_API: OpenWeatherAPI = OpenWeatherAPI()
router: Router = Router()
db: CRUD = CRUD()
constants: Constants = get_constants()
settings: Settings = get_settings()


def get_lan_lon(node: str) -> tuple:
    location = locator.geocode(node)
    return location.latitude, location.longitude


def get_coordinates(nodes: list[str]) -> list[tuple]:
    result = [tuple() for _ in range(len(nodes))]
    for index in range(len(nodes)):
        result[index] = (locator.geocode(nodes[index]).latitude, locator.geocode(nodes[index]).longitude)
    return result


def get_repr_date(date: datetime) -> str:
    return datetime.strftime(date, constants.TIME_PATTERN)


def clc_delta(node1: str, node2: str, transport_type: str) -> int:
    location1, location2 = locator.geocode(node1), locator.geocode(node2)
    coordinates1 = (location1.latitude, location1.longitude)
    coordinates2 = (location2.latitude, location2.longitude)
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
              f"Автор: {node_data.journey_author}\n"
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


@router.message(Command(commands=["delete_journey"]), StateFilter(default_state))
async def create_journey_command(message: Message, state: FSMContext,
                                 sessionmaker: sessionmaker[Session]):
    text = message.text.split()
    if len(text) != 2:
        await message.answer("Введи команду в формате /delete_journey {ID}.")
        return
    journey_id = int(text[1])
    journey = db.get_journey_by_id(sessionmaker, journey_id)
    if journey is None:
        await message.answer("Данное путешествие не найдено.")
    elif journey.journey_author != str(message.from_user.id):
        await message.answer("Вы не являетесь автором мероприятия.")
    else:
        db.remove_journey(sessionmaker, journey)
        await message.answer("Путешествие успешно удалено.")


@router.message(Command(commands=["journey"]), StateFilter(default_state))
async def create_journey_command(message: Message, state: FSMContext,
                                 sessionmaker: sessionmaker[Session]):
    text = message.text.split()
    if len(text) != 2:
        await message.answer("Введи команду в формате /journey {ID}.")
        return
    journey_id = int(text[1])
    journey = db.get_journey_by_id(sessionmaker, journey_id)
    if journey is None:
        await message.answer("Данное путешествие не найдено.")
    elif str(message.from_user.id) not in journey.journey_participants:
        await message.answer("Вы не являетесь участником этого мероприятия.")
    else:
        await message.answer(get_data(journey, sessionmaker))


@router.message(Command(commands=["my_journeys"]), StateFilter(FSMMyJourneys.my_journeys))
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


@router.callback_query(StateFilter(default_state))
async def FSMMyJourneysError(callback: CallbackQuery, state: FSMContext,
                             sessionmaker: sessionmaker[Session]):
    await callback.message.delete()
    await state.clear()


@router.callback_query(StateFilter(FSMMyJourneys.my_journeys))
async def FSMMyJourneys1(callback: CallbackQuery, state: FSMContext,
                         sessionmaker: sessionmaker[Session]):
    user_id = callback.from_user.id
    journeys = db.get_my_journeys(sessionmaker, str(user_id))
    index = (await state.get_data())["index"]
    n = len(journeys)
    match callback.data:
        case "left":
            if index == 0:
                await callback.answer("Это самое первое путешествие!")
            else:
                text = get_data(journeys[index - 1], sessionmaker)
                await state.update_data(index=(index - 1))
                await callback.message.edit_text(text, reply_markup=keyboard_switch)
            await state.set_state(FSMMyJourneys.my_journeys)
            await callback.answer()
        case "right":
            if index == n - 1:
                await callback.answer("Это самое последнее путешествие!")
            else:
                text = get_data(journeys[index + 1], sessionmaker)
                await state.update_data(index=(index + 1))
                await callback.message.edit_text(text, reply_markup=keyboard_switch)
            await state.set_state(FSMMyJourneys.my_journeys)
            await callback.answer()
        case "add_friend":
            if str(user_id) != journeys[index].journey_author:
                await callback.message.answer("Вы не являетесь автором путешествия!")
                await state.set_state(FSMMyJourneys.my_journeys)
            else:
                await callback.message.answer("Укажи ID друга в системе.")
                await state.set_state(FSMMyJourneys.add_friend)
            await callback.answer()
        case "remove_friend":
            if str(user_id) != journeys[index].journey_author:
                await callback.message.answer("Вы не являетесь автором путешествия!")
                await state.set_state(FSMMyJourneys.my_journeys)
            else:
                await callback.message.answer("Укажи ID друга в системе.")
                await state.set_state(FSMMyJourneys.remove_friend)
            await callback.answer()
        case "route_image":
            await callback.message.answer("Выберите формат вашего устройства.", reply_markup=keyboard_resolution)
            await state.set_state(FSMMyJourneys.get_image)
            await callback.answer()
        case "weather":
            await callback.message.answer("Пожалуйста, подождите.")
            nodes = clc_nodes(journeys[index], sessionmaker).split("\n")
            for index in range(0, len(nodes), 2):
                curr = nodes[index]
                if index == 0:
                    curr = curr[8:]
                    curr = curr.split(":", 1)
                else:
                    curr = curr.replace(" до ", "*", 1)
                    curr = curr.replace(": с ", "*", 1)
                    curr = curr.split("*", 2)
                node = curr[0]
                dates = [datetime.strptime(curr[pos].strip(), constants.TIME_PATTERN) for pos in range(1, len(curr))]
                day, night = -float("inf"), float("inf")
                lat, lon = get_lan_lon(node)
                forecast = await open_weather_API.get_forecast(lat, lon)
                for dt, temp in forecast:
                    if any(dt.date() == d.date() for d in dates) and (
                            constants.six_hour_am <= dt.time() <= constants.eight_hour_pm):
                        day = max(day, temp)
                    elif any(dt.date() == d.date() for d in dates):
                        night = min(night, temp)
                if day == -float("inf"):
                    nodes[index] += "\nДневная температура: Нет данных"
                else:
                    nodes[index] += f"\nДневная температура: {round(day, 1)} °C"

                if night == float("inf"):
                    nodes[index] += "\nНочная температура: Нет данных"
                else:
                    nodes[index] += f"\nНочная температура: {round(night, 1)} °C"

            await callback.message.answer("\n".join(nodes))
            await callback.answer()
            await state.set_state(FSMMyJourneys.my_journeys)

        case "cancel":
            await callback.message.delete()
            await state.clear()


@router.message(StateFilter(FSMMyJourneys.get_image))
async def FSMMyJourneys_get_image(message: Message, state: FSMContext, sessionmaker: sessionmaker[Session]):
    await message.answer("Пожалуйста, подождите.")
    resolution = (800, 800) if message.text == "Телефон" else (1920, 1080)
    journeys = db.get_my_journeys(sessionmaker, str(message.from_user.id))
    index = (await state.get_data())["index"]
    journey_data = journeys[index]
    user = db.get_user_by_id(sessionmaker, str(message.from_user.id))
    nodes = [f"{user.city}, {user.country}"] + journey_data.journey_path
    nodes = get_coordinates(nodes)
    map_image = StaticMap(*resolution, url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
    for index in range(1, len(nodes)):
        lan1, log1 = nodes[index - 1][::-1]
        lan2, log2 = nodes[index][::-1]
        map_image.add_marker(CircleMarker(nodes[index - 1][::-1], "red", 20))
        map_image.add_marker(CircleMarker(nodes[index][::-1], "red", 20))
        transport_type = "car" if journey_data.transport_type != "Пешком" else "pedestrian"
        route = (await tom_tom_API.get_route(lan1, log1, lan2, log2, transport_type))[::10]
        for pos in range(1, len(route)):
            lan1, log1 = route[pos - 1]["longitude"], route[pos - 1]["latitude"]
            lan2, log2 = route[pos]["longitude"], route[pos]["latitude"]
            map_image.add_line(Line([(lan1, log1), (lan2, log2)], "green", width=5))
    image = map_image.render()
    bio = BytesIO()
    image.save(bio, "PNG")
    photo = BufferedInputFile(file=bio.getvalue(), filename="path.png")
    caption = get_data(journey_data, sessionmaker)
    await message.answer_photo(photo=photo, caption=caption)
    await state.set_state(FSMMyJourneys.my_journeys)


@router.message(StateFilter(FSMMyJourneys.add_friend))
async def FSMMyJourneys_add_friend(message: Message, state: FSMContext, sessionmaker: sessionmaker[Session]):
    user_id = message.from_user.id
    friend_id = message.text
    friend = db.get_user_by_id(sessionmaker, str(friend_id))
    journeys = db.get_my_journeys(sessionmaker, str(user_id))
    index = (await state.get_data())["index"]
    if friend is None:
        await message.answer("Такой пользователь не найден в системе!")
        await message.delete()
        await state.set_state(FSMMyJourneys.my_journeys)
    elif friend_id in journeys[index].journey_participants:
        await message.answer("Пользователь уже участвует в мероприятие!")
        await message.delete()
        await state.set_state(FSMMyJourneys.my_journeys)
    else:
        await message.answer("Друг успешно добавлен!")
        await message.delete()
        db.add_friend_in_journey(sessionmaker, friend_id, journeys[index].journey_id)
        await state.set_state(FSMMyJourneys.my_journeys)


@router.message(StateFilter(FSMMyJourneys.remove_friend))
async def FSMMyJourneys_remove_friend(message: Message, state: FSMContext, sessionmaker: sessionmaker[Session]):
    user_id = message.from_user.id
    friend_id = message.text
    friend = db.get_user_by_id(sessionmaker, str(friend_id))
    journeys = db.get_my_journeys(sessionmaker, str(user_id))
    index = (await state.get_data())["index"]
    if str(user_id) == friend_id:
        await message.answer("Нельзя удалить автора, нужно полностью удалить путешествие.")
        await message.delete()
        await state.set_state(FSMMyJourneys.my_journeys)
    elif friend is None:
        await message.answer("Такой пользователь не найден в системе!")
        await message.delete()
        await state.set_state(FSMMyJourneys.my_journeys)
    elif friend_id not in journeys[index].journey_participants:
        await message.answer("Пользователь не участвует в мероприятие!")
        await message.delete()
        await state.set_state(FSMMyJourneys.my_journeys)
    else:
        await message.answer("Друг успешно удалён!")
        await message.delete()
        db.remove_friend_from_journey(sessionmaker, friend_id, journeys[index].journey_id)
        await state.set_state(FSMMyJourneys.my_journeys)


@router.message(StateFilter(FSMCreateJourney.get_name))
async def FSMCreateJourney1(message: Message, state: FSMContext):
    await state.update_data(journey_name=message.text)
    await message.answer("Теперь укажи тип транспорта. (От этого будет зависеть время в пути)",
                         reply_markup=keyboard_transport_type)
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
                             "Сколько пунктов ты хочешь посетить в процессе путешествия?")
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
                "Если захочешь удалить поездку, используй /delete_journey {ID}\n\n")
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

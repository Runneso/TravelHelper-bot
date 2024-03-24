from services import GeoPyAPI, InviteTokensAPI, TomTomAPI, OpenWeatherAPI
from states import MyJourneysStates
from keyboards import my_journeys_handler_keyboards, create_journey_handler_keyboard
from database import CRUD, Journeys, InviteTokens, AddNode
from config import get_settings, Settings, get_constants, Constants
from lexicon import my_journeys_handler_lexicon, create_journey_handler_lexicon

from datetime import timedelta, datetime
from io import BytesIO
from math import ceil

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import StateFilter, Command, CommandObject
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker, Session
from staticmap import StaticMap, Line, CircleMarker
from loguru import logger

openweather_API: OpenWeatherAPI = OpenWeatherAPI()
tom_tom_API: TomTomAPI = TomTomAPI()
geo_py_API: GeoPyAPI = GeoPyAPI()
invite_tokens_API: InviteTokensAPI = InviteTokensAPI()

lexicon = my_journeys_handler_lexicon
lexicon2 = create_journey_handler_lexicon
keyboard = my_journeys_handler_keyboards
keyboard2 = create_journey_handler_keyboard

my_journeys: Router = Router()
db: CRUD = CRUD()

settings: Settings = get_settings()
constants: Constants = get_constants()


def get_repr_date(date: datetime) -> str:
    """

    :param date:
    :return:
    """
    return datetime.strftime(date, constants.TIME_PATTERN)


def clc_nodes(journey_data: Journeys) -> str:
    """

    :param journey_data:
    :return:
    """
    datetime_start = journey_data.datetime_start
    node_start = f"Выезд - {journey_data.path[0]}: {get_repr_date(datetime_start)}"
    nodes = [node_start]
    for index in range(1, len(journey_data.path)):
        datetime_start += timedelta(days=int(journey_data.time_in_path[index - 1]))
        nodes.append(
            f"{journey_data.path[index]}: с {get_repr_date(datetime_start)} до {get_repr_date(datetime_start + timedelta(days=int(journey_data.delays[index - 1])))}")
        datetime_start += timedelta(days=int(journey_data.delays[index - 1]))
    return f"\n{lexicon.Emojis.down}\n".join(nodes)


def get_journey_data(journey_data: Journeys, sessionmaker: sessionmaker[Session]) -> str:
    """

    :param journey_data:
    :param sessionmaker:
    :return:
    """
    answer = (f"ID: {journey_data.id}\n"
              f"Название: {journey_data.name}\n"
              f"Автор: {journey_data.author}\n"
              f"Тип транспорта: {journey_data.transport_type}\n"
              f"Участники путешествия: {', '.join([db.get_user_by_id(sessionmaker, user_id).username + f' (ID: {user_id})' for user_id in journey_data.participants])}\n")
    return answer + f"\n<b>ПУТЬ {lexicon.Emojis.map} </b>\n" + clc_nodes(journey_data)


def get_user_data(message: Message) -> dict[str]:
    """

    :param message:
    :return:
    """
    data = dict()
    data["user_id"]: str = str(message.from_user.id)
    data["username"]: str = str(message.from_user.username)
    data["first_name"]: str = str(message.from_user.first_name)
    data["last_name"]: str = str(message.from_user.last_name)
    data["text"]: str = str(message.text)
    return data


def get_callback_data(callback: CallbackQuery) -> dict[str]:
    """

    :param callback:
    :return:
    """
    data = dict()
    data["user_id"]: str = str(callback.from_user.id)
    data["username"]: str = str(callback.from_user.username)
    data["first_name"]: str = str(callback.from_user.first_name)
    data["last_name"]: str = str(callback.from_user.last_name)
    data["data"]: str = str(callback.data)
    return data


@my_journeys.message(Command(commands=["my_journeys"]), StateFilter(default_state))
async def get_my_journeys(message: Message, state: FSMContext,
                          sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для команды.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    journeys = db.get_my_journeys(sessionmaker, user_data["user_id"])
    if journeys:
        await state.update_data(index=0)
        await message.answer(get_journey_data(journeys[0], sessionmaker), reply_markup=keyboard.kb_switch,
                             parse_mode="HTML")
        await state.set_state(MyJourneysStates.my_journeys)
    else:
        await message.answer(lexicon.Error.no_journeys)


@my_journeys.message(Command(commands=["my_journeys"]), StateFilter(MyJourneysStates.my_journeys))
async def duplicate_menu(message: Message, state: FSMContext):
    """
    Хэндлер для дупликата.
    :param message:
    :param state:
    """
    await message.answer(lexicon.Error.duplicate_menu)


@my_journeys.callback_query(StateFilter(MyJourneysStates.my_journeys),
                            keyboard.Pagination.filter(F.action.in_(["left", "right"])))
async def callback_my_journeys(callback: CallbackQuery, state: FSMContext,
                               sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для передвижения по списку путешествий.
    :param callback:
    :param state:
    :param sessionmaker:
    """
    callback_data = get_callback_data(callback)
    journeys = db.get_my_journeys(sessionmaker, callback_data["user_id"])
    n = len(journeys)
    index = (await state.get_data())["index"]
    action = callback_data["data"]

    if action == "pag:left":
        if index - 1 >= 0:
            index -= 1
            await state.update_data(index=index)
            await callback.message.edit_text(get_journey_data(journeys[index], sessionmaker),
                                             reply_markup=keyboard.kb_switch, parse_mode="HTML")
            await callback.answer()
        else:
            await callback.answer(lexicon.Error.min_index)

    else:
        if index + 1 < n:
            index += 1
            await state.update_data(index=index)
            await callback.message.edit_text(get_journey_data(journeys[index], sessionmaker),
                                             reply_markup=keyboard.kb_switch, parse_mode="HTML")
            await callback.answer()
        else:
            await callback.answer(lexicon.Error.max_index)


@my_journeys.callback_query(StateFilter(MyJourneysStates.my_journeys),
                            keyboard.Pagination.filter(F.action.in_(["add_friend", "remove_friend"])))
async def callback_my_journeys(callback: CallbackQuery, state: FSMContext,
                               sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для управления друзьями.
    :param callback:
    :param state:
    :param sessionmaker:
    :return:
    """
    callback_data = get_callback_data(callback)
    action = callback_data["data"]
    journeys = db.get_my_journeys(sessionmaker, callback_data["user_id"])
    index = (await state.get_data())["index"]

    if callback_data["user_id"] != journeys[index].author:
        await callback.answer(lexicon.Error.no_author)
        return

    if action == "pag:add_friend":
        code = await invite_tokens_API.get_token()
        db.create_token(sessionmaker, InviteTokens(code=code, journey_id=journeys[index].id))
        await callback.message.answer(f"Отправь эту ссылку другу: https://t.me/Travel_Helper_prod_bot?start={code}")
        await callback.answer()
    else:
        participants_ids = list(journeys[index].participants)
        participants_ids.remove(journeys[index].author)
        participants = [db.get_user_by_id(sessionmaker, id).username for id in participants_ids]
        kb_remove = keyboard.get_remove_kb(participants, participants_ids)
        if not kb_remove.keyboard:
            await callback.answer(lexicon.Error.no_friend_to_remove)
        else:
            await callback.message.answer(lexicon.remove_friend_string,
                                          reply_markup=kb_remove)
            await state.set_state(MyJourneysStates.remove_friend)
            await callback.answer()


@my_journeys.message(StateFilter(MyJourneysStates.remove_friend))
async def remove_friend(message: Message, state: FSMContext, sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для удаления друга.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    to_delete = user_data["text"].split("(ID: ")[1][:-1]
    journeys = db.get_my_journeys(sessionmaker, user_data["user_id"])
    index = (await state.get_data())["index"]
    journey_id = journeys[index].id
    db.remove_friend_from_journey(sessionmaker, to_delete, journey_id)
    await message.answer(lexicon.correct_deletion)
    await state.set_state(MyJourneysStates.my_journeys)


@my_journeys.callback_query(StateFilter(MyJourneysStates.my_journeys),
                            keyboard.Pagination.filter(F.action.in_(["route_image"])))
async def callback_my_journeys(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для получения картинки маршрута.
    :param callback:
    :param state:
    :param sessionmaker:
    """
    await callback.message.answer(lexicon.choice_resolution, reply_markup=keyboard.kb_resolution)
    await state.set_state(MyJourneysStates.get_image)
    await callback.answer()


@my_journeys.message(StateFilter(MyJourneysStates.get_image))
async def get_image(message: Message, state: FSMContext, sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения разрешения фото пути.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    await message.answer(lexicon.wait_string)
    resolution = (800, 800) if user_data["text"] == "Телефон" else (1920, 1080)
    journeys = db.get_my_journeys(sessionmaker, str(message.from_user.id))
    index = (await state.get_data())["index"]
    journey_data = journeys[index]
    transport_type = "car" if journey_data.transport_type != "Пешком" else "pedestrian"
    if journey_data.transport_type == "Самолёт":
        transport_type = "airplane"
    array_lan, array_lon = journey_data.lat, journey_data.lon
    coordinates = list()
    for index in range(len(array_lan)):
        coordinates.append((array_lan[index], array_lon[index]))
    map_image = StaticMap(*resolution, url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png")
    for index in range(1, len(coordinates)):

        lat1, lon1 = coordinates[index - 1]
        lat2, lon2 = coordinates[index]
        map_image.add_marker(CircleMarker((lon1, lat1), "red", 20))
        map_image.add_marker(CircleMarker((lon2, lat2), "red", 20))

        if transport_type == "airplane":
            map_image.add_line(Line([(lon1, lat1), (lon2, lat2)], "blue", width=5))
        else:
            route = (await tom_tom_API.get_route(lat1, lon1, lat2, lon2, transport_type))

            if route is None:
                map_image.add_line(Line([(lon1, lat1), (lon2, lat2)], "blue", width=5))
            else:
                route = route[::10]
                for pos in range(1, len(route)):
                    lat3, lon3 = route[pos - 1]["latitude"], route[pos - 1]["longitude"]
                    lat4, lon4 = route[pos]["latitude"], route[pos]["longitude"]
                    map_image.add_line(Line([(lon3, lat3), (lon4, lat4)], "green", width=5))

    image = map_image.render()
    bytes_info = BytesIO()
    image.save(bytes_info, "PNG")
    photo = BufferedInputFile(file=bytes_info.getvalue(), filename="path.png")
    caption = f"\n<b>ПУТЬ {lexicon.Emojis.map} </b>\n" + clc_nodes(journey_data)
    await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML")
    await state.set_state(MyJourneysStates.my_journeys)


@my_journeys.callback_query(StateFilter(MyJourneysStates.my_journeys),
                            keyboard.Pagination.filter(F.action.in_(["weather"])))
async def callback_my_journeys(callback: CallbackQuery, state: FSMContext,
                               sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения погоды.
    :param callback:
    :param state:
    :param sessionmaker:
    """
    callback_data = get_callback_data(callback)
    await callback.message.answer(lexicon.wait_string)
    journeys = db.get_my_journeys(sessionmaker, callback_data["user_id"])
    index = (await state.get_data())["index"]
    journey_data = journeys[index]

    array_lat, array_lon = list(journey_data.lat), list(journey_data.lon)
    start_datetime = journey_data.datetime_start

    temperature = list()
    for index in range(len(array_lat)):
        if index == 0:
            curr_min, curr_max = float("inf"), -float("inf")
            lat, lon = array_lat[index], array_lon[index]
            data = await openweather_API.get_forecast(lat, lon)
            for dt, temp in data:
                if dt.date() == start_datetime.date():
                    curr_min = min(curr_min, temp)
                    curr_max = max(curr_max, temp)
            if curr_min == float("inf") or curr_max == -float("inf"):
                temperature.append((None, None))
            else:
                temperature.append((curr_min, curr_max))
            start_datetime += timedelta(days=journey_data.time_in_path[index - 1])
        else:
            curr_min, curr_max = float("inf"), -float("inf")
            lat, lon = array_lat[index], array_lon[index]
            data = await openweather_API.get_forecast(lat, lon)
            for dt, temp in data:
                if start_datetime.date() <= dt.date() <= (
                        start_datetime + timedelta(days=journey_data.delays[index - 1])).date():
                    curr_min = min(curr_min, temp)
                    curr_max = max(curr_max, temp)
            if curr_min == float("inf") or curr_max == -float("inf"):
                temperature.append((None, None))
            else:
                temperature.append((curr_min, curr_max))
            start_datetime += timedelta(days=journey_data.time_in_path[index - 1])
    answer = clc_nodes(journey_data).split(f"\n{lexicon.Emojis.down}\n")
    for index in range(len(answer)):
        curr_max = temperature[index][1] if temperature[index][1] else "Нет данных"
        curr_min = temperature[index][0] if temperature[index][0] else "Нет данных"
        answer[index] += f"\nМаксимальная температура: {curr_max} °C\n"
        answer[index] += f"Минимальная температура: {curr_min} °C"
    answer = f"\n<b>ПОГОДА {lexicon.Emojis.weather} </b>\n" + f"\n{lexicon.Emojis.down}\n".join(answer)
    await callback.message.answer(answer, parse_mode="HTML")
    await callback.answer()


@my_journeys.callback_query(StateFilter(MyJourneysStates.my_journeys),
                            keyboard.Pagination.filter(F.action.in_(["delete"])))
async def callback_my_journeys(callback: CallbackQuery, state: FSMContext,
                               sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для удаления мероприятия.
    :param callback:
    :param state:
    :param sessionmaker:
    :return:
    """
    callback_data = get_callback_data(callback)
    journeys = sorted(db.get_my_journeys(sessionmaker, str(callback_data["user_id"])), key=lambda x: int(x.id))
    index = (await state.get_data())["index"]
    if journeys[index].author != str(callback_data["user_id"]):
        await callback.answer(lexicon.Error.no_author)
        return
    db.remove_journey(sessionmaker, journeys[index])
    journeys.pop(index)
    if not len(journeys):
        await callback.answer(lexicon.Error.no_journeys_yet)
        await callback.message.delete()
        await state.clear()
    else:
        index -= 1
        await state.update_data(index=index)
        await callback.message.edit_text(get_journey_data(journeys[index], sessionmaker),
                                         reply_markup=keyboard.kb_switch, parse_mode="HTML")
        await callback.answer()


@my_journeys.callback_query(StateFilter(MyJourneysStates.my_journeys),
                            keyboard.Pagination.filter(F.action.in_(["exit"])))
async def callback_my_journeys(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для выхода.
    :param callback:
    :param state:
    """
    await callback.message.delete()
    await callback.message.answer(lexicon.main_menu, reply_markup=keyboard.kb_main_menu)
    await state.clear()


@my_journeys.message(Command(commands=["journey"]), StateFilter(default_state))
async def journey(message: Message, state: FSMContext,
                  sessionmaker: sessionmaker[Session], command: CommandObject):
    """
    Хэндлер для получения путешествия по индификатору.
    :param message:
    :param state:
    :param sessionmaker:
    :param command:
    """
    user_data = get_user_data(message)
    ID = command.args

    if ID is None:
        await message.answer(lexicon.Error.no_id)
    else:
        journeys = db.get_my_journeys(sessionmaker, user_data["user_id"])
        index = None
        for index_i in range(len(journeys)):
            if str(journeys[index_i].id) == str(ID):
                index = index_i
                break
        if index is None:
            await message.answer(lexicon.Error.no_find_journey)
        else:
            await state.update_data(index=index)
            await message.answer(get_journey_data(journeys[index], sessionmaker), reply_markup=keyboard.kb_switch,
                                 parse_mode="HTML")
            await state.set_state(MyJourneysStates.my_journeys)


@my_journeys.callback_query(StateFilter(MyJourneysStates.my_journeys),
                            keyboard.Pagination.filter(F.action.in_(["update"])))
async def update_journey(callback: CallbackQuery, state: FSMContext,
                         sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для обновления данных о путешествие.
    :param callback:
    :param state:
    :param sessionmaker:
    :return:
    """
    callback_data = get_callback_data(callback)
    journeys = sorted(db.get_my_journeys(sessionmaker, str(callback_data["user_id"])), key=lambda x: int(x.id))
    index = (await state.get_data())["index"]

    if str(journeys[index].author) != str(callback_data["user_id"]):
        await callback.answer(lexicon.Error.no_author)
        return

    await callback.message.answer(lexicon.update_string, reply_markup=keyboard.kb_update)
    await state.set_state(MyJourneysStates.get_update_type)
    await callback.answer()


@my_journeys.message(StateFilter(MyJourneysStates.get_update_type))
async def get_update_type(message: Message, state: FSMContext):
    """
    Хэндлер для получения типа правки.
    :param message:
    :param state:
    :return:
    """
    user_data = get_user_data(message)
    update_type = user_data["text"]

    if update_type not in {"Название 🔤", "Тип транспорта 🚘", "Дату начала 📅", "Добавить пункт 🌇"}:
        await message.answer(lexicon.Error.invalid_update_type)
        return

    match update_type:
        case "Название 🔤":
            await message.answer(lexicon.update_name_string)
            await state.set_state(MyJourneysStates.update_name)
        case "Тип транспорта 🚘":
            await message.answer(lexicon.update_transport_type_string, reply_markup=keyboard2.kb_transport_type)
            await state.set_state(MyJourneysStates.update_transport_type)
        case "Дату начала 📅":
            await message.answer(lexicon.update_datetime_start_string)
            await state.set_state(MyJourneysStates.update_datetime_start)
        case "Добавить пункт 🌇":
            await message.answer(lexicon.update_add_node_name_string)
            await state.set_state(MyJourneysStates.add_node_name)


@my_journeys.message(StateFilter(MyJourneysStates.update_name))
async def get_update_name(message: Message, state: FSMContext,
                          sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для обновления названия.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    new_name = user_data["text"]
    journeys = sorted(db.get_my_journeys(sessionmaker, str(user_data["user_id"])), key=lambda x: int(x.id))
    index = (await state.get_data())["index"]
    db.change_journey_name(sessionmaker, journeys[index].id, new_name)
    await message.answer(lexicon.correct_update)
    await state.set_state(MyJourneysStates.my_journeys)


@my_journeys.message(StateFilter(MyJourneysStates.update_transport_type))
async def get_update_transport_type(message: Message, state: FSMContext,
                                    sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для обновления типа транспорта.
    :param message:
    :param state:
    :param sessionmaker:
    :return:
    """
    user_data = get_user_data(message)
    new_transport_type = user_data["text"]
    if new_transport_type not in constants.TRANSPORTS.keys():
        await message.answer(lexicon2.Errors.invalid_transport_type)
        return
    journeys = sorted(db.get_my_journeys(sessionmaker, str(user_data["user_id"])), key=lambda x: int(x.id))
    index = (await state.get_data())["index"]
    db.change_journey_transport_type(sessionmaker, journeys[index].id, new_transport_type)
    await db.recalculate_time_in_path(sessionmaker, journeys[index].id)
    await message.answer(lexicon.correct_update)
    await state.set_state(MyJourneysStates.my_journeys)


@my_journeys.message(StateFilter(MyJourneysStates.update_datetime_start))
async def get_update_datetime_start(message: Message, state: FSMContext,
                                    sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для обновления даты начала.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    new_datetime_start = user_data["text"]
    try:
        new_datetime_start = datetime.strptime(new_datetime_start, constants.TIME_PATTERN)
        journeys = sorted(db.get_my_journeys(sessionmaker, str(user_data["user_id"])), key=lambda x: int(x.id))
        index = (await state.get_data())["index"]
    except Exception as error:
        await message.answer(lexicon2.Errors.invalid_datetime_start)
        logger.error(error)
    else:
        db.change_journey_datetime_start(sessionmaker, journeys[index].id, new_datetime_start)
        await message.answer(lexicon.correct_update)
        await state.set_state(MyJourneysStates.my_journeys)


@my_journeys.message(StateFilter(MyJourneysStates.add_node_name))
async def get_add_node_name(message: Message, state: FSMContext):
    """
    Хэндлер для получения названия нового пункта.
    :param message:
    :param state:
    :return:
    """
    user_data = get_user_data(message)
    node_name = user_data["text"]
    location = await geo_py_API.get_coordinates(node_name)
    if location is None:
        await message.answer(lexicon2.Errors.invalid_node_name)
        return
    await message.answer(lexicon.update_add_node_name_delay)
    await state.update_data(new_node_name=node_name)
    await state.set_state(MyJourneysStates.add_node_delay)


@my_journeys.message(StateFilter(MyJourneysStates.add_node_delay))
async def get_add_node_delay(message: Message, state: FSMContext,
                            sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения времени прибывания на новом пункте.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    node_delay = user_data["text"]
    try:
        node_delay = int(node_delay)
    except Exception as error:
        await message.answer(lexicon2.Errors.invalid_node_delay)
        logger.error(error)
    else:
        journeys = sorted(db.get_my_journeys(sessionmaker, str(user_data["user_id"])), key=lambda x: int(x.id))
        index = (await state.get_data())["index"]
        node_name = (await state.get_data())["new_node_name"]
        lat, lon = (await geo_py_API.get_coordinates(node_name))
        last_distance = await geo_py_API.get_distance((lat, lon), (journeys[index].lat[-1], journeys[index].lon[-1]))
        node_time_in_path = ceil(last_distance / constants.TRANSPORTS[journeys[index].transport_type])
        node = AddNode(name=node_name,
                       delay=node_delay,
                       lat=lat, lon=lon,
                       time_in_path=node_time_in_path)
        db.create_new_node(sessionmaker, journeys[index].id, node)
        await message.answer(lexicon.correct_update)
        await state.set_state(MyJourneysStates.my_journeys)

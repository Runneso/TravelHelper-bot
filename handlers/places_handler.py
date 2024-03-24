from services import TomTomAPI, Place
from states import MyJourneysStates, PlacesHandler
from keyboards import my_journeys_handler_keyboards, places_handler_keyboard
from database import CRUD
from config import get_settings, Settings, get_constants, Constants
from lexicon import places_handler_lexicon

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker, Session


tom_tom_API: TomTomAPI = TomTomAPI()
lexicon = places_handler_lexicon
keyboard = my_journeys_handler_keyboards
keyboard2 = places_handler_keyboard
places: Router = Router()
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


def get_place_text(place: list[Place], node: str) -> str:
    """

    :param place:
    :param node:
    :return:
    """
    result = (f"<b> ОКРУГА 🏘 </b>\n\n"
              f"Пункт: {node}\n\n")
    for p in place:
        curr = (f"Название: {p.name}\n"
                f"Адрес: {p.address}\n"
                f"Телефон: {p.phone_number}\n"
                f"Сайт: {p.url}\n"
                f"Часы работы: {p.opening_hours}\n\n")
        result += curr
    return result


@places.callback_query(StateFilter(MyJourneysStates.my_journeys),
                       keyboard.Pagination.filter(F.action.in_(["places"])))
async def callback_places(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для получения списка мест.
    :param callback:
    :param state:
    """
    await callback.message.answer(lexicon.place_type_string, reply_markup=keyboard2.kb_place_type)
    await state.set_state(PlacesHandler.get_place_type)
    await callback.answer()


@places.message(StateFilter(PlacesHandler.get_place_type))
async def get_place_type(message: Message, state: FSMContext,
                         sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения типа места.
    :param message:
    :param state:
    :param sessionmaker:
    :return:
    """
    user_data = get_user_data(message)
    place_type = user_data["text"]
    journeys = db.get_my_journeys(sessionmaker, user_data["user_id"])
    index = (await state.get_data())["index"]
    journey_data = journeys[index]

    if place_type not in {"Рестораны/Кафе", "Отели/Мотели", "Достопримечательности"}:
        await message.answer(lexicon.Error.invalid_place_type)
        return
    await state.update_data(place_type=place_type)
    nodes = list()

    match place_type:
        case "Рестораны/Кафе":
            for index in range(journey_data.length + 1):
                lat, lon = journey_data.lat[index], journey_data.lon[index]
                nodes.append(await tom_tom_API.get_restaurants(lat, lon))
        case "Отели/Мотели":
            for index in range(journey_data.length + 1):
                lat, lon = journey_data.lat[index], journey_data.lon[index]
                nodes.append(await tom_tom_API.get_hotels(lat, lon))

        case "Достопримечательности":
            for index in range(journey_data.length + 1):
                lat, lon = journey_data.lat[index], journey_data.lon[index]
                nodes.append(await tom_tom_API.get_attractions(lat, lon))

    await state.update_data(iiindex=0)
    await message.answer(get_place_text(nodes[0], journey_data.path[0]), reply_markup=keyboard.kb_place_slider,
                         parse_mode="HTML")
    await state.set_state(PlacesHandler.slider)


@places.callback_query(StateFilter(PlacesHandler.slider),
                       keyboard.Pagination.filter(F.action.in_(["llleft", "rrright"])))
async def callback_places_move(callback: CallbackQuery, state: FSMContext,
                               sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для передвижения по списку мест.
    :param callback:
    :param state:
    :param sessionmaker:
    """
    callback_data = get_callback_data(callback)
    journeys = db.get_my_journeys(sessionmaker, callback_data["user_id"])
    index = (await state.get_data())["index"]
    iiindex = (await state.get_data())["iiindex"]
    place_type = (await state.get_data())["place_type"]
    journey_data = journeys[index]
    action = callback_data["data"]

    nodes = list()
    match place_type:
        case "Рестораны/Кафе":
            for index in range(journey_data.length + 1):
                lat, lon = journey_data.lat[index], journey_data.lon[index]
                nodes.append(await tom_tom_API.get_restaurants(lat, lon))
        case "Отели/Мотели":
            for index in range(journey_data.length + 1):
                lat, lon = journey_data.lat[index], journey_data.lon[index]
                nodes.append(await tom_tom_API.get_hotels(lat, lon))

        case "Достопримечательности":
            for index in range(journey_data.length + 1):
                lat, lon = journey_data.lat[index], journey_data.lon[index]
                nodes.append(await tom_tom_API.get_attractions(lat, lon))

    if action == "pag:llleft":
        if iiindex - 1 >= 0:
            iiindex -= 1
            await callback.message.edit_text(get_place_text(nodes[iiindex], journey_data.path[iiindex]),
                                             reply_markup=keyboard.kb_place_slider,
                                             parse_mode="HTML")

            await state.update_data(iiindex=iiindex)
            await callback.answer()
        else:
            await callback.answer(lexicon.Error.first_node)
    else:
        if iiindex + 1 < len(nodes):
            iiindex += 1
            await callback.message.edit_text(get_place_text(nodes[iiindex], journey_data.path[iiindex]),
                                             reply_markup=keyboard.kb_place_slider,
                                             parse_mode="HTML")
            await state.update_data(iiindex=iiindex)
            await callback.answer()
        else:
            await callback.answer(lexicon.Error.last_node)


@places.callback_query(StateFilter(PlacesHandler.slider),
                       keyboard.Pagination.filter(F.action.in_(["eeexit"])))
async def callback_places_exit(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для выхода.
    :param callback:
    :param state:
    """
    await callback.message.delete()
    await state.set_state(MyJourneysStates.my_journeys)
    await callback.answer()

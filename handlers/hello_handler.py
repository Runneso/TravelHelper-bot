from database import CRUD, Users
from config import get_settings, Settings, get_constants, Constants
from lexicon import hello_handler_lexicon
from states import HelloHandler
from keyboards import hello_handler_keyboards
from services import GeoPyAPI, TomTomAPI

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter, Command, CommandObject
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

api = TomTomAPI()

geo_py_API: GeoPyAPI = GeoPyAPI()
states = HelloHandler()
keyboards = hello_handler_keyboards
lexicon = hello_handler_lexicon
hello_router: Router = Router()
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


@hello_router.message(CommandStart(), StateFilter(default_state))
async def start_command(message: Message, state: FSMContext,
                        sessionmaker: sessionmaker[Session], command: CommandObject):
    """
    Хэндлер для команды.
    :param message:
    :param state:
    :param sessionmaker:
    :param command:
    """
    if command.args:
        user_data = get_user_data(message)
        already_created = db.get_user_by_id(sessionmaker, user_data["user_id"])
        token = db.get_token_by_value(sessionmaker, command.args)
        journey = db.get_journey_by_id(sessionmaker, token.journey_id) if token else None
        if already_created is None:
            await message.answer(lexicon.Errors.invalid_invite)
        elif token is None:
            await message.answer(lexicon.Errors.invalid_token)
        elif user_data["user_id"] in journey.participants:
            await message.answer(lexicon.Errors.already_take_part)
        else:
            db.add_friend_in_journey(sessionmaker, user_data["user_id"], token.journey_id)
            db.remove_token(sessionmaker, token)
            await message.answer(lexicon.correct_invite)
    else:
        user_data = get_user_data(message)
        already_created = db.get_user_by_id(sessionmaker, user_data["user_id"])
        if already_created is None:
            if user_data["username"]:
                await message.answer(lexicon.hello_new_user_username(user_data["username"]))
            else:
                await message.answer(
                    lexicon.hello_new_first_name_last_name(user_data["first_name"], user_data["last_name"]))
            await state.set_state(HelloHandler.age)
        else:
            if user_data["username"]:
                await message.answer(lexicon.hello_username(user_data["username"]))
            else:
                await message.answer(
                    lexicon.hello_first_name_last_name(user_data["first_name"], user_data["last_name"]))


@hello_router.message(Command(commands=["help"]), StateFilter(default_state))
async def help_command(message: Message, state: FSMContext):
    """
    Хэндлер для команды.
    :param message:
    :param state:
    """
    await message.answer(hello_handler_lexicon.help_string)


@hello_router.message(StateFilter(HelloHandler.age))
async def get_age(message: Message, state: FSMContext):
    """
    Хэндлер для получения возраста пользователя.
    :param message:
    :param state:
    """
    user_data = get_user_data(message)
    try:
        age = int(user_data["text"])
    except Exception as error:
        logger.error(error)
        await message.answer(lexicon.Errors.invalid_age)
    else:
        await state.update_data(age=age)
        await message.answer(lexicon.location_string, reply_markup=keyboards.kb_location)
        await state.set_state(HelloHandler.location)


@hello_router.message(F.text, StateFilter(HelloHandler.location))
async def get_text_location(message: Message, state: FSMContext):
    """
    Хэндлер для получения локации текстом.
    :param message:
    :param state:
    """
    user_data = get_user_data(message)
    text = user_data["text"]
    location = await geo_py_API.get_coordinates(text)
    if location is None:
        await message.answer(lexicon.Errors.invalid_text_location, reply_markup=keyboards.kb_location)
    else:
        latitude, longitude = location
        await state.update_data(location=text)
        await state.update_data(lat=latitude)
        await state.update_data(lon=longitude)
        await message.answer(lexicon.biography_string, reply_markup=hello_handler_keyboards.rkb)
        await state.set_state(HelloHandler.biography)


@hello_router.message(F.location, StateFilter(HelloHandler.location))
async def get_location_location(message: Message, state: FSMContext):
    """
    Хэндлер для получения локации геометкой.
    :param message:
    :param state:
    """
    latitude = round(message.location.latitude, 2)
    longitude = round(message.location.longitude, 2)
    location = (await geo_py_API.get_geocode(latitude, longitude))
    await state.update_data(location=location.address)
    await state.update_data(lat=latitude)
    await state.update_data(lon=longitude)
    await message.answer(lexicon.biography_string, reply_markup=hello_handler_keyboards.rkb)
    await state.set_state(HelloHandler.biography)


@hello_router.message(StateFilter(HelloHandler.biography))
async def get_biography(message: Message, state: FSMContext,
                        sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения биографии.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    await state.update_data(biography=message.text)
    data = await state.get_data()
    await message.answer(hello_handler_lexicon.info_string)
    username = user_data["username"] if user_data["username"] else str(user_data["first_name"]) + str(user_data[
                                                                                                          "last_name"])
    user = Users(user_id=user_data["user_id"], username=username, age=data["age"],
                 location=data["location"], lat=data["lat"], lon=data["lon"],
                 biography=data["biography"])
    db.create_user(sessionmaker, user)
    await state.clear()


@hello_router.message(Command(commands=["cancel"]))
async def total_cancel(message: Message, state: FSMContext):
    """
    Хэндлер для команды.
    :param message:
    :param state:
    :return:
    """
    curr_state = await state.get_state()
    if curr_state is None:
        await message.answer(lexicon.cancel)
        return
    count, message_id = 0, message.message_id
    while count < 10 and message_id > 0:
        try:
            await message.chat.delete_message(message_id)
            count += 1
        except Exception as error:
            logger.error(error)
        message_id -= 1
    await message.answer(lexicon.cancel)
    await state.clear()

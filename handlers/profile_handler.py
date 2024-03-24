from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from keyboards import profile_hanlder_keyboard, hello_handler_keyboards
from database import CRUD
from config import get_settings, Settings, get_constants, Constants
from lexicon import profile_handler_lexicon, hello_handler_lexicon
from services import GeoPyAPI
from states import ProfileHandler

geo_py_API: GeoPyAPI = GeoPyAPI()
keyboard = profile_hanlder_keyboard
keyboard2 = hello_handler_keyboards
lexicon = profile_handler_lexicon
lexicon2 = hello_handler_lexicon
profile_router: Router = Router()
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
    data["username"]: str = str(message.from_user.username)
    data["first_name"]: str = str(message.from_user.first_name)
    data["last_name"]: str = str(message.from_user.last_name)
    data["text"]: str = str(message.text)
    return data


@profile_router.message(Command(commands=["profile"]), StateFilter(default_state))
async def profile_command(message: Message, state: FSMContext,
                          sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для команды.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    user = db.get_user_by_id(sessionmaker, user_data["user_id"])
    await message.answer(lexicon.profile(user), parse_mode="HTML", reply_markup=keyboard.kb_change_profile)
    await state.set_state(ProfileHandler.callback)


@profile_router.callback_query(StateFilter(ProfileHandler.callback),
                               keyboard.Pagination.filter(F.action.in_(["age"])))
async def change_age(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для получения нового возраста.
    :param callback:
    :param state:
    """
    await callback.message.answer(lexicon.age_string)
    await state.set_state(ProfileHandler.age)
    await callback.answer()


@profile_router.callback_query(StateFilter(ProfileHandler.callback),
                               keyboard.Pagination.filter(F.action.in_(["biography"])))
async def change_biography(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для получения новой биографии.
    :param callback:
    :param state:
    """
    await callback.message.answer(lexicon.biography_string)
    await state.set_state(ProfileHandler.biography)
    await callback.answer()


@profile_router.callback_query(StateFilter(ProfileHandler.callback),
                               keyboard.Pagination.filter(F.action.in_(["location"])))
async def change_location(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для получения новой локации.
    :param callback:
    :param state:
    """
    await callback.message.answer(lexicon.location_string, reply_markup=keyboard2.kb_location)
    await state.set_state(ProfileHandler.location)
    await callback.answer()


@profile_router.callback_query(StateFilter(ProfileHandler.callback),
                               keyboard.Pagination.filter(F.action.in_(["exit"])))
async def exit(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для выхода.
    :param callback:
    :param state:
    """
    await callback.message.delete()
    await state.clear()
    await callback.answer()


@profile_router.message(StateFilter(ProfileHandler.age))
async def get_age(message: Message, state: FSMContext,
                  sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для обновления возраста.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    try:
        age = int(user_data["text"])
    except Exception as error:
        logger.error(error)
        await message.answer(lexicon2.Errors.invalid_age)
    else:
        db.change_age(sessionmaker, user_data["user_id"], age)
        await message.answer(lexicon.correct_age)
        await state.set_state(ProfileHandler.callback)


@profile_router.message(StateFilter(ProfileHandler.biography))
async def get_biography(message: Message, state: FSMContext,
                        sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для обновления биографии.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    biography = (user_data["text"])
    db.change_biography(sessionmaker, user_data["user_id"], biography)
    await message.answer(lexicon.correct_biography)
    await state.set_state(ProfileHandler.callback)


@profile_router.message(StateFilter(ProfileHandler.location), F.location)
async def get_location(message: Message, state: FSMContext,
                       sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для обновления локации с помощью геометки.
    :param message:
    :param state:
    :param sessionmaker:
    """
    latitude = round(message.location.latitude, 2)
    longitude = round(message.location.longitude, 2)
    location = (await geo_py_API.get_geocode(latitude, longitude))
    location = location.address
    db.change_location(sessionmaker, str(message.from_user.id), latitude, longitude, location)
    await message.answer(lexicon.correct_location)
    await state.set_state(ProfileHandler.callback)


@profile_router.message(StateFilter(ProfileHandler.location), F.text)
async def get_location(message: Message, state: FSMContext,
                       sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для обновления локации с помощью текста.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    text = user_data["text"]
    location = await geo_py_API.get_coordinates(text)
    if location is None:
        await message.answer(lexicon2.Errors.invalid_text_location, reply_markup=keyboard2.kb_location)
    else:
        latitude, longitude = location
        location = text
        db.change_location(sessionmaker, str(message.from_user.id), latitude, longitude, location)
        await message.answer(lexicon.correct_location)
        await state.set_state(ProfileHandler.callback)

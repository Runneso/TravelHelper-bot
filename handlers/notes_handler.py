from services import MoneyConverterAPI
from states import MyJourneysStates, NotesHandler, SeeNotes
from keyboards import my_journeys_handler_keyboards, notes_handler_keyboards
from database import CRUD, Notes
from config import get_settings, Settings, get_constants, Constants
from lexicon import notes_handler_lexicon

from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker, Session

money_converter_API: MoneyConverterAPI = MoneyConverterAPI()
lexicon = notes_handler_lexicon
keyboard = my_journeys_handler_keyboards
keyboard2 = notes_handler_keyboards
notes: Router = Router()
db: CRUD = CRUD()
settings: Settings = get_settings()
constants: Constants = get_constants()

translate = {"Денежная трата": "money",
             "Текстовая записка": "text",
             "Фотография": "photo"}


def get_money_message(note: Notes,
                      sessionmaker: sessionmaker[Session]):
    """

    :param note:
    :param sessionmaker:
    :return:
    """
    money = str(note.value).split('.')
    user = db.get_user_by_id(sessionmaker, note.author)
    return (f"Автор: {user.username} (ID: {note.author})\n"
            f"Дата создания: {datetime.strftime(note.date, constants.TIME_PATTERN)}\n"
            f"Приватность: {'публичная' if note.isPublic else 'частная'}\n"
            f"Сумма: {money[0]}.{money[1][:2]} $")


def get_text_message(note: Notes,
                     sessionmaker: sessionmaker[Session]):
    """

    :param note:
    :param sessionmaker:
    :return:
    """
    user = db.get_user_by_id(sessionmaker, note.author)
    return (f"Автор: {user.username} (ID: {note.author})\n"
            f"Дата создания: {datetime.strftime(note.date, constants.TIME_PATTERN)}\n"
            f"Приватность: {'публичная' if note.isPublic else 'частная'}\n"
            f"Контент: {note.value}")


def get_caption_message(note: Notes,
                        sessionmaker: sessionmaker[Session]):
    """

    :param note:
    :param sessionmaker:
    :return:
    """
    user = db.get_user_by_id(sessionmaker, note.author)
    return (f"Автор: {user.username} (ID: {note.author})\n"
            f"Дата создания: {datetime.strftime(note.date, constants.TIME_PATTERN)}\n"
            f"Приватность: {'публичная' if note.isPublic else 'частная'}\n")


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


@notes.callback_query(StateFilter(MyJourneysStates.my_journeys),
                      keyboard.Pagination.filter(F.action.in_(["add_note"])))
async def add_note(callback: CallbackQuery, state: FSMContext,
                   sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для добавления заметки.
    :param callback:
    :param state:
    :param sessionmaker:
    """
    callback_data = get_callback_data(callback)
    journeys = db.get_my_journeys(sessionmaker, callback_data["user_id"])
    index = (await state.get_data())["index"]
    await callback.message.answer(lexicon.type_string, reply_markup=keyboard2.kb_type)
    await state.update_data(author=callback_data["user_id"])
    await state.update_data(journey_id=journeys[index].id)
    await callback.answer()
    await state.set_state(NotesHandler.get_type)


@notes.message(StateFilter(NotesHandler.get_type))
async def get_type(message: Message, state: FSMContext):
    """
    Хэндлер для получения типа заметки.
    :param message:
    :param state:
    """
    user_data = get_user_data(message)
    if user_data["text"] not in {"Денежная трата", "Текстовая записка", "Фотография"}:
        await message.answer(lexicon.Error.invalid_type)
    else:
        await state.update_data(note_type=translate[user_data["text"]])
        await message.answer(lexicon.privacy_string, reply_markup=keyboard2.kb_privacy)
        await state.set_state(NotesHandler.get_privacy)


@notes.message(StateFilter(NotesHandler.get_privacy))
async def get_privacy(message: Message, state: FSMContext):
    """
    Хэндлер для получения приватности заметки.
    :param message:
    :param state:
    """
    user_data = get_user_data(message)
    if user_data["text"] not in {"Публичная", "Приватная"}:
        await message.answer(lexicon.Error.invalid_privacy)
    else:
        note_type = (await state.get_data())["note_type"]
        await state.update_data(isPublic=user_data["text"] == "Публичная")
        match note_type:
            case "text":
                await message.answer(lexicon.text_string)
                await state.set_state(NotesHandler.get_text)
            case "photo":
                await message.answer(lexicon.photo_string)
                await state.set_state(NotesHandler.get_photo)
            case "money":
                await message.answer(lexicon.money_string)
                await state.set_state(NotesHandler.get_money)


@notes.message(F.photo, StateFilter(NotesHandler.get_photo))
async def get_photo(message: Message, state: FSMContext,
                    sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения фото.
    :param message:
    :param state:
    :param sessionmaker:
    """
    data = await state.get_data()
    photo = message.photo
    value = photo[0].model_dump()["file_id"]
    note = Notes(author=data["author"], isPublic=data["isPublic"],
                 journey_id=data["journey_id"], note_type=data["note_type"],
                 value=value)
    db.create_note(sessionmaker, note)
    await message.answer(lexicon.correct_creation)
    await state.set_state(MyJourneysStates.my_journeys)


@notes.message(StateFilter(NotesHandler.get_money))
async def get_money(message: Message, state: FSMContext,
                    sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения денежный заметки.
    :param message:
    :param state:
    :param sessionmaker:
    """
    data = await state.get_data()
    text = message.text.split()
    if len(text) != 2 or (not text[0].isdigit()) or money_converter_API.clc_usd(text[0], text[1]) is None:
        await message.answer(lexicon.Error.invalid_currency)
    else:
        value = money_converter_API.clc_usd(text[0], text[1])
        note = Notes(author=data["author"], isPublic=data["isPublic"],
                     journey_id=data["journey_id"], note_type=data["note_type"],
                     value=value)
        db.create_note(sessionmaker, note)
        await message.answer(lexicon.correct_creation)
        await state.set_state(MyJourneysStates.my_journeys)


@notes.message(StateFilter(NotesHandler.get_text))
async def get_text(message: Message, state: FSMContext,
                   sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения текстовой заметки.
    :param message:
    :param state:
    :param sessionmaker:
    """
    data = await state.get_data()
    value = message.text
    note = Notes(author=data["author"], isPublic=data["isPublic"],
                 journey_id=data["journey_id"], note_type=data["note_type"],
                 value=value)
    db.create_note(sessionmaker, note)
    await message.answer(lexicon.correct_creation)
    await state.set_state(MyJourneysStates.my_journeys)


@notes.callback_query(StateFilter(MyJourneysStates.my_journeys),
                      keyboard.Pagination.filter(F.action.in_(["see_note"])))
async def see_note(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для просмотра заметки.
    :param callback:
    :param state:
    """
    await callback.message.answer(lexicon.type_string, reply_markup=keyboard2.kb_type)
    await state.set_state(SeeNotes.get_type)
    await callback.answer()


@notes.message(StateFilter(SeeNotes.get_type))
async def get_type(message: Message, state: FSMContext,
                   sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для получения типа заметки.
    :param message:
    :param state:
    :param sessionmaker:
    """
    user_data = get_user_data(message)
    if user_data["text"] not in {"Денежная трата", "Текстовая записка", "Фотография"}:
        await message.answer(lexicon.Error.invalid_type)
    else:
        journeys = db.get_my_journeys(sessionmaker, user_data["user_id"])
        index = (await state.get_data())["index"]
        all_notes = db.get_notes_by_type_and_journey_id(sessionmaker, str(journeys[index].id), translate[message.text])
        need_notes = sorted([note for note in all_notes if note.isPublic or note.author == user_data["user_id"]],
                            key=lambda x: x.id)
        if need_notes:
            await state.update_data(iindex=0)
            curr = need_notes[0]
            match curr.note_type:
                case "photo":
                    await state.update_data(note_type="photo")
                    await message.answer_photo(photo=curr.value, caption=get_caption_message(curr, sessionmaker),
                                               reply_markup=keyboard.kb_note_slider)
                case "text":
                    await state.update_data(note_type="text")
                    await message.answer(get_text_message(curr, sessionmaker), reply_markup=keyboard.kb_note_slider)
                case "money":
                    await state.update_data(note_type="money")
                    await message.answer(get_money_message(curr, sessionmaker), reply_markup=keyboard.kb_note_slider)
            await state.update_data(jounrey_iid=str(journeys[index].id))
            await state.set_state(SeeNotes.slider)
        else:
            await message.answer(lexicon.Error.no_notes)
            await state.set_state(MyJourneysStates.my_journeys)


@notes.callback_query(StateFilter(SeeNotes.slider),
                      keyboard.Pagination.filter(F.action.in_(["lleft", "rright"])))
async def callback_move(callback: CallbackQuery, state: FSMContext,
                        sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для передвижения по списку заметок.
    :param callback:
    :param state:
    :param sessionmaker:
    """
    callback_data = get_callback_data(callback)
    jounrey_iid = (await state.get_data())["jounrey_iid"]
    iindex = (await state.get_data())["iindex"]
    note_type = (await state.get_data())["note_type"]
    all_notes = db.get_notes_by_type_and_journey_id(sessionmaker, jounrey_iid, note_type)
    need_notes = sorted([note for note in all_notes if note.isPublic or note.author == callback_data["user_id"]],
                        key=lambda x: x.id)
    action = callback_data["data"]

    if action == "pag:lleft":
        if iindex - 1 >= 0:
            iindex -= 1
            await state.update_data(iindex=iindex)
            match note_type:
                case "photo":
                    photo = InputMediaPhoto(media=need_notes[iindex].value,
                                            caption=get_caption_message(need_notes[iindex], sessionmaker))
                    await callback.message.edit_media(photo, reply_markup=keyboard.kb_note_slider)
                case "text":
                    await callback.message.edit_text(get_text_message(need_notes[iindex], sessionmaker),
                                                     reply_markup=keyboard.kb_note_slider)
                case "money":
                    await callback.message.edit_text(get_money_message(need_notes[iindex], sessionmaker),
                                                     reply_markup=keyboard.kb_note_slider)
            await callback.answer()
        else:
            await callback.answer(lexicon.Error.first_note)
    else:
        if iindex + 1 < len(need_notes):
            iindex += 1
            await state.update_data(iindex=iindex)
            match note_type:
                case "photo":
                    photo = InputMediaPhoto(media=need_notes[iindex].value,
                                            caption=get_caption_message(need_notes[iindex], sessionmaker))
                    await callback.message.edit_media(photo, reply_markup=keyboard.kb_note_slider)
                case "text":
                    await callback.message.edit_text(get_text_message(need_notes[iindex], sessionmaker),
                                                     reply_markup=keyboard.kb_note_slider)
                case "money":
                    await callback.message.edit_text(get_money_message(need_notes[iindex], sessionmaker),
                                                     reply_markup=keyboard.kb_note_slider)
            await callback.answer()
        else:
            await callback.answer(lexicon.Error.last_note)


@notes.callback_query(StateFilter(SeeNotes.slider),
                      keyboard.Pagination.filter(F.action.in_(["remove_note"])))
async def callback_remove_note(callback: CallbackQuery, state: FSMContext,
                               sessionmaker: sessionmaker[Session]):
    """
    Хэндлер для удаления заметок.
    :param callback:
    :param state:
    :param sessionmaker:
    """
    callback_data = get_callback_data(callback)
    jounrey_iid = (await state.get_data())["jounrey_iid"]
    iindex = (await state.get_data())["iindex"]
    note_type = (await state.get_data())["note_type"]
    all_notes = db.get_notes_by_type_and_journey_id(sessionmaker, jounrey_iid, note_type)
    need_notes = sorted([note for note in all_notes if note.isPublic or note.author == callback_data["user_id"]],
                        key=lambda x: x.id)
    db.remove_note(sessionmaker, need_notes[iindex])
    need_notes.pop(iindex)

    if not len(need_notes):
        await callback.answer(lexicon.Error.no_notes_yet)
        await callback.message.delete()
        await state.set_state(MyJourneysStates.my_journeys)
    else:
        iindex -= 1
        await state.update_data(iindex=iindex)
        match note_type:
            case "photo":
                photo = InputMediaPhoto(media=need_notes[iindex].value,
                                        caption=get_caption_message(need_notes[iindex], sessionmaker))
                await callback.message.edit_media(photo, reply_markup=keyboard.kb_note_slider)
            case "text":
                await callback.message.edit_text(get_text_message(need_notes[iindex], sessionmaker),
                                                 reply_markup=keyboard.kb_note_slider)
            case "money":
                await callback.message.edit_text(get_money_message(need_notes[iindex], sessionmaker),
                                                 reply_markup=keyboard.kb_note_slider)
        await callback.answer()


@notes.callback_query(StateFilter(SeeNotes.slider),
                      keyboard.Pagination.filter(F.action.in_(["eexit"])))
async def callback_cancel(callback: CallbackQuery, state: FSMContext):
    """
    Хэндлер для выхода.
    :param callback:
    :param state:
    """
    await callback.message.delete()
    await state.set_state(MyJourneysStates.my_journeys)
    await callback.answer()

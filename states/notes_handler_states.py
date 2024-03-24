from aiogram.fsm.state import State, StatesGroup


class NotesHandler(StatesGroup):
    get_type = State()
    get_privacy = State()
    get_photo = State()
    get_money = State()
    get_text = State()


class SeeNotes(StatesGroup):
    get_type = State()
    slider = State()

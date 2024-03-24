from aiogram.fsm.state import StatesGroup, State


class HelloHandler(StatesGroup):
    age = State()
    location = State()
    biography = State()

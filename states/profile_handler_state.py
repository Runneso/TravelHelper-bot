from aiogram.fsm.state import State, StatesGroup


class ProfileHandler(StatesGroup):
    callback = State()
    age = State()
    biography = State()
    location = State()

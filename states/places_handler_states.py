from aiogram.fsm.state import State, StatesGroup


class PlacesHandler(StatesGroup):
    get_place_type = State()
    slider = State()

from aiogram.fsm.state import State, StatesGroup


class CreateJourneyHandler(StatesGroup):
    name = State()
    transport_type = State()
    datetime_start = State()
    length = State()
    node_name = State()
    node_delay = State()

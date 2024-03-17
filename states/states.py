from aiogram.fsm.state import State, StatesGroup


class FSMStart(StatesGroup):
    get_age = State()
    get_location = State()
    get_bio = State()


class FSMCreateJourney(StatesGroup):
    get_name = State()
    get_transport_type = State()
    get_datetime_start = State()
    get_journey_length = State()
    get_node_name = State()
    get_node_delay = State()


class FSMMyJourneys(StatesGroup):
    my_journeys = State()
    add_friend = State()
    remove_friend = State()
    get_image = State()

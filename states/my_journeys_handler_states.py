from aiogram.fsm.state import State, StatesGroup


class MyJourneysStates(StatesGroup):
    my_journeys = State()
    remove_friend = State()
    get_image = State()

    get_update_type = State()
    update_name = State()
    update_transport_type = State()
    update_datetime_start = State()
    add_node_name = State()
    add_node_delay = State()

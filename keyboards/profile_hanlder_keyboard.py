from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Pagination(CallbackData, prefix="pag"):
    action: str


bt_age = InlineKeyboardButton(text="Сменить возраст 🔢", callback_data=Pagination(action="age").pack())
bt_biography = InlineKeyboardButton(text="Сменить биографию ℹ️", callback_data=Pagination(action="biography").pack())
bt_location = InlineKeyboardButton(text="Сменить местоположение 🗺", callback_data=Pagination(action="location").pack())
bt_exit = InlineKeyboardButton(text="Выйти", callback_data=Pagination(action="exit").pack())

kb_change_profile = InlineKeyboardMarkup(inline_keyboard=[[bt_age, bt_biography], [bt_location], [bt_exit]])

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from lexicon import my_journeys_handler_lexicon

lexicon = my_journeys_handler_lexicon


class Pagination(CallbackData, prefix="pag"):
    action: str


def get_remove_kb(participants: list[str], participants_ids: list[str]):
    kb_remove = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[], one_time_keyboard=True,
                                    input_field_placeholder="Отправь друга для удаления.")
    for index in range(len(participants)):
        bt_remove = KeyboardButton(text=f"{participants[index]} (ID: {participants_ids[index]})")
        kb_remove.keyboard.append([bt_remove])
    return kb_remove


bt_left = InlineKeyboardButton(text=lexicon.Emojis.left, callback_data=Pagination(action="left").pack())
bt_right = InlineKeyboardButton(text=lexicon.Emojis.right, callback_data=Pagination(action="right").pack())
bt_cancel = InlineKeyboardButton(text="Выйти", callback_data=Pagination(action="exit").pack())
bt_add_friend = InlineKeyboardButton(text="Добавить друга 👥", callback_data=Pagination(action="add_friend").pack())
bt_remove_friend = InlineKeyboardButton(text="Удалить друга 👤", callback_data=Pagination(action="remove_friend").pack())
bt_get_route_image = InlineKeyboardButton(text="Путь 🗺",
                                          callback_data=Pagination(action="route_image").pack())
bt_add_note = InlineKeyboardButton(text="Добавить заметку ✍️",
                                   callback_data=Pagination(action="add_note").pack())
bt_see_note = InlineKeyboardButton(text="Заметки 🗒",
                                   callback_data=Pagination(action="see_note").pack())
bt_delete = InlineKeyboardButton(text="Удалить ❌",
                                 callback_data=Pagination(action="delete").pack())
bt_places = InlineKeyboardButton(text="Округа 🏘", callback_data=Pagination(action="places").pack())
bt_update = InlineKeyboardButton(text="Изменить 🔄", callback_data=Pagination(action="update").pack())
bt_weather = InlineKeyboardButton(text="Погода " + lexicon.Emojis.weather,
                                  callback_data=Pagination(action="weather").pack())
kb_switch = InlineKeyboardMarkup(
    inline_keyboard=[[bt_left, bt_right], [bt_add_friend, bt_remove_friend], [bt_add_note, bt_see_note],
                     [bt_get_route_image, bt_weather],
                     [bt_places],
                     [bt_delete, bt_update],
                     [bt_cancel]])

button_mobile = KeyboardButton(text="Телефон")
button_pc = KeyboardButton(text="Компьютер")
button_another = KeyboardButton(text="Иное")
kb_resolution = ReplyKeyboardMarkup(resize_keyboard=True,
                                    keyboard=[[button_mobile, button_pc, button_another]], one_time_keyboard=True,
                                    input_field_placeholder="Выберите формат устройства.")

bt_left_note = InlineKeyboardButton(text=lexicon.Emojis.left, callback_data=Pagination(action="lleft").pack())
bt_right_note = InlineKeyboardButton(text=lexicon.Emojis.right, callback_data=Pagination(action="rright").pack())
bt_cancel_note = InlineKeyboardButton(text="Выйти", callback_data=Pagination(action="eexit").pack())
bt_remove_note = InlineKeyboardButton(text="Удалить заметку 🧽",
                                      callback_data=Pagination(action="remove_note").pack())

kb_note_slider = InlineKeyboardMarkup(
    inline_keyboard=[[bt_left_note, bt_right_note], [bt_remove_note], [bt_cancel_note]])

bt_left_place = InlineKeyboardButton(text=lexicon.Emojis.left, callback_data=Pagination(action="llleft").pack())
bt_right_place = InlineKeyboardButton(text=lexicon.Emojis.right, callback_data=Pagination(action="rrright").pack())
bt_cancel_place = InlineKeyboardButton(text="Выйти", callback_data=Pagination(action="eeexit").pack())

kb_place_slider = InlineKeyboardMarkup(inline_keyboard=[[bt_left_place, bt_right_place], [bt_cancel_place]])

bt_create_journey = KeyboardButton(text="/create_journey")
bt_my_journeys = KeyboardButton(text="/my_journeys")
bt_help = KeyboardButton(text="/help")
bt_profile = KeyboardButton(text="/profile")

kb_main_menu = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=[[bt_help], [bt_create_journey, bt_my_journeys], [bt_profile]],
                                   one_time_keyboard=True,
                                   input_field_placeholder="Выберите действие."
                                   )

bt_update_name = KeyboardButton(text="Название 🔤")
bt_update_transport_type = KeyboardButton(text="Тип транспорта 🚘")
bt_update_datetime_start = KeyboardButton(text="Дату начала 📅")
bt_add_node = KeyboardButton(text="Добавить пункт 🌇")

kb_update = ReplyKeyboardMarkup(resize_keyboard=True,
                                keyboard=[[bt_update_name, bt_update_transport_type], [bt_update_datetime_start],
                                          [bt_add_node]],
                                one_time_keyboard=True,
                                input_field_placeholder="Выберите действие."
                                )

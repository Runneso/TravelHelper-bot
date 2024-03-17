from aiogram import types
from strings import left, right, weather

button_location = types.KeyboardButton(text="Отправить геопозицию.", request_location=True)
keyboard_location = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button_location]])

button_left = types.InlineKeyboardButton(text=left, callback_data="left")
button_right = types.InlineKeyboardButton(text=right, callback_data="right")
button_cancel = types.InlineKeyboardButton(text="Выйти", callback_data="cancel")
button_add_friend = types.InlineKeyboardButton(text="Добавить друга 👥", callback_data="add_friend")
button_remove_friend = types.InlineKeyboardButton(text="Удалить друга 👤", callback_data="remove_friend")
button_get_route_image = types.InlineKeyboardButton(text="Получить картинку пути 🗺", callback_data="route_image")
button_update = types.InlineKeyboardButton(text="Изменить данные", callback_data="update")
button_notes = types.InlineKeyboardButton(text="Заметки", callback_data="notes")
button_weather = types.InlineKeyboardButton(text="Погода " + weather, callback_data="weather")
keyboard_switch = types.InlineKeyboardMarkup(
    inline_keyboard=[[button_left, button_right], [button_add_friend, button_remove_friend], [button_get_route_image],
                     [button_weather],
                     [button_cancel]])

button_foot = types.KeyboardButton(text="Пешком")
button_car = types.KeyboardButton(text="Автомобиль")
button_airplane = types.KeyboardButton(text="Самолёт")
button_another = types.KeyboardButton(text="Иное")
keyboard_transport_type = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [button_foot, button_car, button_airplane, button_another]])

button_mobile = types.KeyboardButton(text="Телефон")
button_pc = types.KeyboardButton(text="Компьютер")
keyboard_resolution = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                keyboard=[[button_mobile, button_pc, button_another]])

from aiogram import types
from strings import left, right,cancel

button_location = types.KeyboardButton(text="Отправить геопозицию.", request_location=True)
keyboard_location = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button_location]])

button_left = types.InlineKeyboardButton(text=left, callback_data="left")
button_right = types.InlineKeyboardButton(text=right, callback_data="right")
button_cancel = types.InlineKeyboardButton(text=cancel,callback_data="cancel")
keyboard_switch = types.InlineKeyboardMarkup(inline_keyboard=[[button_left, button_right],[button_cancel]])

button_foot = types.KeyboardButton(text="Пешком")
button_car = types.KeyboardButton(text="Автомобиль")
button_airplane = types.KeyboardButton(text="Самолёт")
button_another = types.KeyboardButton(text="Иное")
keyboard_transport_type = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [button_foot, button_car, button_airplane, button_another]])

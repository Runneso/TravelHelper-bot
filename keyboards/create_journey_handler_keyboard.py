from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

button_foot = KeyboardButton(text="Пешком")
button_car = KeyboardButton(text="Автомобиль")
button_airplane = KeyboardButton(text="Самолёт")
button_another = KeyboardButton(text="Иное")
kb_transport_type = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [button_foot, button_car, button_airplane, button_another]], one_time_keyboard=True,
                                        input_field_placeholder="Отправь тип трансопрта.")

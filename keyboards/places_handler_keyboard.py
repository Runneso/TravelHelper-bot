from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

bt_restaurants = KeyboardButton(text="Рестораны/Кафе")
bt_hotels = KeyboardButton(text="Отели/Мотели")
bt_attractions = KeyboardButton(text="Достопримечательности")

kb_place_type = ReplyKeyboardMarkup(resize_keyboard=True,
                                    keyboard=[[bt_restaurants, bt_hotels], [bt_attractions]], one_time_keyboard=True,
                                    input_field_placeholder="Выберите тип заметки.")

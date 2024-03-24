from aiogram.types import KeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup

bt_location = KeyboardButton(text="Отправить геопозицию", request_location=True)
kb_location = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[bt_location]], one_time_keyboard=True,
                                  input_field_placeholder="Отправь геопозицию.")

rkb = ReplyKeyboardRemove()

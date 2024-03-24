from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

bt_money = KeyboardButton(text="Денежная трата")
bt_text = KeyboardButton(text="Текстовая записка")
bt_photo = KeyboardButton(text="Фотография")
kb_type = ReplyKeyboardMarkup(resize_keyboard=True,
                              keyboard=[[bt_money, bt_text, bt_photo]], one_time_keyboard=True,
                              input_field_placeholder="Выберите тип заметки.")

bt_public = KeyboardButton(text="Публичная")
bt_private = KeyboardButton(text="Приватная")
kb_privacy = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[[bt_public, bt_private]], one_time_keyboard=True,
                                 input_field_placeholder="Выберите вариант приватности.")

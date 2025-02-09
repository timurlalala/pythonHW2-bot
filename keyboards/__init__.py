from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


target_confirmation_keyboard = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="Ввести свою цель"),
        KeyboardButton(text="Сохранить")
    ]],
    resize_keyboard=True,
    input_field_placeholder="Выберите ответ",
    one_time_keyboard=True
)
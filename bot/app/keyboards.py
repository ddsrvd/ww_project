from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
#Reply клавиатура
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Найти трек")],
    [KeyboardButton(text="Добавить трек")],
],resize_keyboard = True)

find = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Поиск по автору")],
    [KeyboardButton(text="Поиск по треку")],
],resize_keyboard = True)


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Найти трек")],
    [KeyboardButton(text="Добавить трек")],
    [KeyboardButton(text="Написать/Посмотреть комментарий")],
], resize_keyboard=True)

find = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Поиск по автору")],
    [KeyboardButton(text="Поиск по треку")],
    [KeyboardButton(text="назад")],
], resize_keyboard=True)

none_author = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="нет автора")],
], resize_keyboard=True)

answer = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Написать комментарий")],
    [KeyboardButton(text="Посмотреть комментарии")],
    [KeyboardButton(text="Другой трек")],
], resize_keyboard=True)


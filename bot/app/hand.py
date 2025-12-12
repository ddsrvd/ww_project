from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.fsm.context import FSMContext

from typing import List
import app.keyboards as kb
import app.States as st
from db import db_api

router = Router()

class Song:
    def __init__(self, name, username, comment):
        self.name = name
        self.username = username
        self.comment = comment

    def get_song_name(self):
        return self.name

    def get_song_comment(self):
        return self.comment



class Handlers:
    a: List[Song] = []
    def __init__(self, router: Router):
        self.router = router
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start, Command("start"))
        #self.router.message.register(self.help, Command("help"))
        self.router.message.register(self.new_song, F.text == "Добавить трек")
        self.router.message.register(self.new_song2, st.Create.get_name)
        self.router.message.register(self.new_song3, st.Create.get_comment)

        self.router.message.register(self.find_song, F.text == "Найти трек")
        self.router.message.register(self.find_song_a, F.text == "Поиск по автору")
        self.router.message.register(self.find_song_a1, st.Search.s_author)
        self.router.message.register(self.find_song_t, F.text == "Поиск по треку")
        self.router.message.register(self.find_song_t1, st.Search.s_name)

    async def start(self, message: types.Message):
        user_name = message.from_user.first_name

        #create new user in table "users"

        welcome_text = f"""
        Привет, {user_name}! 👋

        Добро пожаловать в нашего бота!
        Я помогу тебе с...

        Доступные команды:
        /help - Помощь
        /about - О боте
                """

        await message.answer(welcome_text, reply_markup=kb.main)


    async def new_song(self, message: types.Message, state: FSMContext):
        await message.answer("Введите название трека")
        #Проверка на корректность и наличие в бд
        await state.set_state(st.Create.get_name)

    async def new_song2(self, message: types.Message, state: FSMContext):
        await state.set_state(st.Create.get_comment)
        await message.answer("Введите рецензию")
        # Проверка на корректность
        await state.update_data(get_name=message.text)

    async def new_song3(self, message: types.Message, state: FSMContext):
        await state.update_data(get_comment=message.text)
        data = await state.get_data()
        #Здесь должно быть добавление в бд

        await message.answer(f"Трек успешно добавлен! \n {data["get_name"]} \n {data["get_comment"]}")
        await state.clear()



    async def find_song(self, message: types.Message):
        await message.answer("Выберите как хотите искать", reply_markup=kb.find)

    async def find_song_a(self, message: types.Message, state: FSMContext):
        await state.set_state(st.Search.s_author)
        await message.answer("Введите исполнителя")

    async def find_song_a1(self, message: types.Message, state: FSMContext):
        await state.update_data(s_author=message.text)
        data = await state.get_data()
        res = db_api.find_song(data["s_author"], type_search=db_api.FindBy.AUTHOR)
        if res:
            await message.answer("Вот треки, автор которых наиболее совпадает с вашим запросом:")
            for i in res:
                await message.answer(await self.print_song(i))
        else:
            await message.answer("К сожалению, по вашему запросу не нашлось ни одного трека!")
        await state.clear()

    async def find_song_t(self, message: types.Message, state: FSMContext):
        await state.set_state(st.Search.s_name)
        await message.answer("Введите название")

    async def find_song_t1(self, message: types.Message, state: FSMContext):
        await state.update_data(s_name=message.text)
        data = await state.get_data()
        res = db_api.find_song(data["s_name"], type_search=db_api.FindBy.NAME)
        if res:
            await message.answer("Вот треки наиболее совпадающие с вашим запросом:")
            for i in res:
                await message.answer(await self.print_song(i))
        else:
            await message.answer("К сожалению, по вашему запросу не нашлось ни одного трека!")
        await state.clear()

    async def print_song(self, song):
        if song["author"]:
            return f'ID трека: {song["song_id"]}\nНазвание трека: {song["name_song"]}\nАвтор: {song["author"]}'
        else:
            return f'ID трека: {song["song_id"]}\nНазвание трека: {song["name_song"]}\nАвтор: неизвестно'


handlers = Handlers(router)

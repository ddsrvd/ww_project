from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

import random
import string
from typing import List
import app.keyboards as kb
import app.States as st
from app.db_client import client as db_api
from app.client_worker import check_text 

router = Router()

class Handlers:
    def __init__(self, router: Router):
        self.router = router
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start, Command("start"))
        self.router.message.register(self.main_menu, st.UserMenu.MAIN_MENU)
        self.router.message.register(self.new_song1, st.Create.get_name)
        self.router.message.register(self.new_song2, st.Create.get_author)
        self.router.message.register(self.search, st.UserMenu.SEARCHING)
        self.router.message.register(self.create_review, st.UserMenu.CREATING_REVIEW)
        self.router.message.register(self.create_review2, st.Create_rev.id_song)
        self.router.message.register(self.create_review3, st.Create_rev.get_comment)
        self.router.message.register(self.find_song_a1, st.Search.s_author)
        self.router.message.register(self.find_song_t1, st.Search.s_name)
        
        # Новые хэндлеры для авторизации и рецензий
        self.router.message.register(self.get_auth_code, Command("code"))
        self.router.message.register(self.get_auth_code, F.text == "Получить код для сайта")
        self.router.message.register(self.get_my_reviews, Command("myreviews"))
        self.router.message.register(self.get_my_reviews, F.text == "Мои рецензии")

    async def start(self, message: types.Message, state: FSMContext):
        user_name = message.from_user.first_name
        user_id = str(message.from_user.id)
        if not await db_api.user_in_db(user_id):
            await db_api.create_user(user_name, user_id)

        welcome_text = f"""
        Привет, {user_name}!

        Добро пожаловать в нашего бота!
        Я помогу тебе с...

        Доступные команды:
        Получить код для входа на сайт
        Написать/посмотреть рецензии уже написанные вами рецензии()
        """

        await message.answer(welcome_text)
        await state.set_state(st.UserMenu.MAIN_MENU)
        await message.answer("ГЛАВНОЕ МЕНЮ", reply_markup=kb.my_reviews)

    async def main_menu(self, message: types.Message, state: FSMContext):
        if message.text == "Добавить трек":
            await message.answer("Введите название трека", reply_markup=ReplyKeyboardRemove())
            await state.set_state(st.Create.get_name)

        elif message.text == "Найти трек":
            await message.answer("Выберите как хотите искать", reply_markup=kb.find)
            await state.set_state(st.UserMenu.SEARCHING)

        elif message.text == "Написать/Посмотреть комментарий":
            await message.answer("Введите id трека", reply_markup=ReplyKeyboardRemove())
            await state.set_state(st.UserMenu.CREATING_REVIEW)
        
        elif message.text == "Мои рецензии":
            await self.get_my_reviews(message)
        
        elif message.text == "Получить код для сайта":
            await self.get_auth_code(message)

    async def new_song1(self, message: types.Message, state: FSMContext):
        # БЕЗ проверки названия
        await state.set_state(st.Create.get_author)
        await message.answer("Введите автора или нажмите 'нет автора'", reply_markup=kb.none_author)
        await state.update_data(get_name=message.text)

    async def new_song2(self, message: types.Message, state: FSMContext):
        # БЕЗ проверки автора
        if message.text == "нет автора":
            await state.update_data(get_author=None)
        else:
            await state.update_data(get_author=message.text)

        data = await state.get_data()
        if await db_api.song_in_db(data["get_name"], data["get_author"]):
            await message.answer("Такой трек уже есть в базе данных, попробуйте еще раз!", reply_markup=kb.my_reviews)
        else:
            await db_api.create_song(data["get_name"], data["get_author"])
            new_song = await db_api.song_in_db(data["get_name"], data["get_author"])
            if new_song:
                await message.answer("Трек успешно добавлен!", reply_markup=kb.my_reviews)
                await message.answer(f'ID трека: {new_song}\nНазвание трека: {data["get_name"]}\nАвтор: {data["get_author"]}')
            else:
                await message.answer("Трек не добавился!", reply_markup=kb.my_reviews)
        await state.set_state(st.UserMenu.MAIN_MENU)

    async def create_review(self, message: types.Message, state: FSMContext):
        await message.answer(await self.print_song(await db_api.get_song(message.text)))
        await state.set_state(st.Create_rev.id_song)
        await message.answer('Выберите действие', reply_markup=kb.answer)
        await state.update_data(id_song=message.text)

    async def create_review2(self, message: types.Message, state: FSMContext):
        if message.text == "Написать комментарий":
            await message.answer("Введите комментарий", reply_markup=ReplyKeyboardRemove())
            await state.set_state(st.Create_rev.get_comment)

        elif message.text == "Посмотреть комментарии":
            data = await state.get_data()
            res = await db_api.get_song_review(data["id_song"])
            await message.answer("Комментарии:")
            num = 1
            if res:
                for i in res:
                    await message.answer(f'{num}) {i[1]}: {i[2]}')
                    num += 1
            else:
                await message.answer("Комментариев пока нет")
            await state.set_state(st.Create_rev.id_song)

        elif message.text == "Другой трек":
            await message.answer("ГЛАВНОЕ МЕНЮ", reply_markup=kb.my_reviews)
            await state.set_state(st.UserMenu.MAIN_MENU)

    async def create_review3(self, message: types.Message, state: FSMContext):
        await message.answer("Подождите немного! Идет проверка вашего комментария.....")
        if check_text(message.text):
            await message.answer("❌ Комментарий содержит нецензурную лексику. Пожалуйста, измените текст.")
            await state.set_state(st.Create_rev.get_comment)
            return
        
        user_name = message.from_user.first_name
        user_tg_id = message.from_user.id
        user_id_1 = await db_api.user_in_db(user_tg_id)
        if user_id_1:
            user_id = user_id_1[0]
        else:
            await message.answer("Ошибка", reply_markup=kb.answer)

        await state.update_data(get_comment=message.text)
        data = await state.get_data()
        await db_api.create_review(user_name, str(user_id), str(data["id_song"]), str(data["get_comment"]))
        await state.set_state(st.Create_rev.id_song)
        await message.answer("✅ Комментарий добавлен!", reply_markup=kb.answer)

    async def search(self, message: types.Message, state: FSMContext):
        if message.text == "Поиск по треку":
            await state.set_state(st.Search.s_name)
            await message.answer("Введите название", reply_markup=ReplyKeyboardRemove())

        elif message.text == "Поиск по автору":
            await state.set_state(st.Search.s_author)
            await message.answer("Введите исполнителя", reply_markup=ReplyKeyboardRemove())

        elif message.text == "назад":
            await message.answer("Возвращаемся в главное меню", reply_markup=kb.my_reviews)
            await state.set_state(st.UserMenu.MAIN_MENU)

    async def find_song_a1(self, message: types.Message, state: FSMContext):
        await state.update_data(s_author=message.text)
        data = await state.get_data()
        type_search = db_api.FindBy.AUTHOR
        res = await db_api.find_song(data["s_author"], type_search=type_search)
        if res:
            await message.answer("Вот треки, автор которых наиболее совпадает с вашим запросом:")
            for i in res:
                await message.answer(await self.print_song(i))
        else:
            await message.answer("К сожалению, по вашему запросу не нашлось ни одного трека!")
        await message.answer("Выберите действие", reply_markup=kb.find)
        await state.set_state(st.UserMenu.SEARCHING)

    async def find_song_t1(self, message: types.Message, state: FSMContext):
        await state.update_data(s_name=message.text)
        data = await state.get_data()
        type_search = db_api.FindBy.NAME
        res = await db_api.find_song(data["s_name"], type_search=type_search)
        if res:
            await message.answer("Вот треки наиболее совпадающие с вашим запросом:")
            for i in res:
                await message.answer(await self.print_song(i))
        else:
            await message.answer("К сожалению, по вашему запросу не нашлось ни одного трека!")
        await message.answer("Выберите действие", reply_markup=kb.find)
        await state.set_state(st.UserMenu.SEARCHING)
    
    # НОВЫЙ МЕТОД: Генерация кода для сайта
    async def get_auth_code(self, message: types.Message):
        """Генерирует временный код для авторизации на сайте"""
        user_name = message.from_user.first_name
        user_tg_id = str(message.from_user.id)
        username = message.from_user.username or user_name
        
        # Генерируем простой код (4 буквы/цифры)
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        try:
            # Используем SimpleClient для вызова API
            result = await db_api.create_auth_code(user_tg_id, username, code)
            
            if result and result.get("success"):
                # Отправляем пользователю
                await message.answer(
                    f"🔐 <b>Ваш код для входа на сайт:</b>\n\n"
                    f"<code>{code}</code>\n\n"
                    f"🌐 Перейдите на сайт и введите его\n"
                    f"👤 Будет использовано имя: {user_name}\n\n"
                    f"<i>После использования код станет недействительным</i>",
                    parse_mode="HTML"
                )
            else:
                await message.answer("❌ Ошибка генерации кода. Попробуйте снова.")
        except Exception as e:
            print(f"Error creating auth code: {e}")
            await message.answer("❌ Ошибка соединения с сервером. Попробуйте позже.")
    
    # НОВЫЙ МЕТОД: Показать все рецензии пользователя
    async def get_my_reviews(self, message: types.Message):
        """Показать все рецензии пользователя (и с сайта, и из бота)"""
        user_tg_id = str(message.from_user.id)
        
        try:
            # Используем SimpleClient для получения рецензий
            result = await db_api.get_user_reviews(user_tg_id)
            
            if not result or not result.get("success"):
                await message.answer("📝 У вас пока нет рецензий")
                return
            
            reviews = result.get("reviews", [])
            
            if not reviews:
                await message.answer("📝 У вас пока нет рецензий")
                return
            
            await message.answer(f"📚 Ваши рецензии ({len(reviews)}):")
            
            for i, review in enumerate(reviews, 1):
                song_name = review.get("song_name", "Неизвестная песня")
                song_author = review.get("song_author", "Неизвестен")
                review_text = review.get("review_text", "")
                song_id = review.get("song_id", "")
                review_id = review.get("review_id", "")
                
                await message.answer(
                    f"{i}. 🎵 <b>{song_name}</b>\n"
                    f"   👨‍🎤 Исполнитель: {song_author}\n"
                    f"   💬 <i>{review_text}</i>\n"
                    f"   🆔 ID песни: {song_id} | ID рецензии: {review_id}",
                    parse_mode="HTML"
                )
            
        except Exception as e:
            print(f"Error getting user reviews: {e}")
            await message.answer("Ошибка при получении рецензий. Попробуйте позже.")

    async def print_song(self, song):
        if song[2]:
            return f'ID трека: {song[0]}\nНазвание трека: {song[1]}\nАвтор: {song[2]}'
        else:
            return f'ID трека: {song[0]}\nНазвание трека: {song[1]}\nАвтор: неизвестно'

handlers = Handlers(router)
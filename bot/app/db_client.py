import aiohttp
import asyncio
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv() 

class SimpleClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("DB_API_URL")  

    async def _get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def _post(self, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:  
                return await response.json()

    async def user_in_db(self, user_tg_id):
        return await self._get(f"/user_in_db/{user_tg_id}")

    async def create_user(self, user_name, user_tg_id):
        return await self._get("/create_user", {"user_name": user_name, "user_tg_id": user_tg_id})

    async def song_in_db(self, name_song, author=None):
        params = {"name_song": name_song}
        if author:
            params["author"] = author
        return await self._get("/song_in_db", params)

    async def create_song(self, name_song, author=None):
        params = {"name_song": name_song}
        if author:
            params["author"] = author
        return await self._get("/create_song", params)

    async def get_song(self, song_id):
        return await self._get(f"/get_song/{song_id}")

    async def get_song_review(self, song_id):
        return await self._get(f"/get_song_review/{song_id}")

    async def create_review(self, user_name, user_id, song_id, comment):
        params = {
            "user_name": user_name,
            "user_id": user_id,
            "song_id": song_id,
            "comment": comment
        }
        return await self._get("/create_review", params)

    async def find_song(self, query, type_search="name"):
        return await self._get("/find_song", {"query": query, "type_search": type_search})

    async def create_auth_code(self, user_tg_id: str, username: str, code: str, expires_minutes: int = 5):
        """Создает временный код для авторизации через API"""
        return await self._post("/create_auth_code", {
            "user_tg_id": user_tg_id,
            "username": username,
            "code": code,
            "expires_minutes": expires_minutes
        })

    async def verify_auth_code(self, code: str):
        """Проверяет временный код через API"""
        return await self._post("/verify_auth_code", {"code": code})

    async def get_user_reviews(self, user_tg_id: str):
        """Получает все рецензии пользователя через API"""
        return await self._get(f"/user_reviews/{user_tg_id}")

    class FindBy:
        AUTHOR = "author"
        NAME = "name"

client = SimpleClient()
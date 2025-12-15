from fastapi import FastAPI, Query
import uvicorn
import asyncio

from db_api import db_api

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/user_in_db/{user_tg_id}")
async def user_in_db(user_tg_id: str):
    return await db_api.user_in_db(user_tg_id)

@app.get("/create_user")
async def create_user(user_name: str, user_tg_id: str):
    return await db_api.create_user(user_name, user_tg_id)

@app.get("/song_in_db")
async def song_in_db(name_song: str, author: str = None):
    return await db_api.song_in_db(name_song, author)

@app.get("/create_song") 
async def create_song(name_song: str, author: str = None):
    return db_api.create_song(name_song, author)

@app.get("/get_song/{song_id}")
async def get_song(song_id: int):
    return await db_api.get_song(song_id)

@app.get("/get_song_review/{song_id}")
async def get_song_review(song_id: int):
    return await db_api.get_song_review(song_id)

@app.get("/create_review")
async def create_review(user_name: str, user_id: str, song_id: str, comment: str): 
    db_api.create_review(user_name, user_id, song_id, comment)
    return True

@app.get("/find_song")
async def find_song(query: str, type_search: str = "name"):
    result = await db_api.find_song(query, type_search=type_search)
    return result

@app.get("/get_findby")
async def get_findby():
    return {
        "AUTHOR": "author",
        "NAME": "name"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

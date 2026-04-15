from fastapi import FastAPI, Query, Body, HTTPException
import uvicorn
import asyncio
import secrets
import time
from typing import List, Dict, Any

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

@app.post("/create_web_song") 
async def create_web_song(
    name_song: str = Body(...),  
    author: str = Body(None)
):
    return db_api.create_song(name_song, author)

@app.get("/get_song/{song_id}")
async def get_song(song_id: int):
    return await db_api.get_song(song_id)

@app.get("/get_song_review/{song_id}")
async def get_song_review(song_id: int):
    return await db_api.get_song_review(song_id)

@app.get("/create_review")
async def create_review(user_name: str, user_id: str, song_id: str, comment: str): 
    result = db_api.create_review(user_name, user_id, song_id, comment)
    return {"success": result}

@app.post("/create_web_review")
async def create_web_review(
    song_id: str = Body(...),
    comment: str = Body(...),
    user_tg_id: str = Body(...)  
):
    # Находим пользователя в БД по user_tg_id
    user_info = await db_api.user_in_db(user_tg_id)
    
    if not user_info:
        return {"success": False, "error": "User not found. Please register in the bot first."}
    
    user_id = user_info[0]  # реальный user_id из БД
    user_name = user_info[1]  # имя из Telegram
    
    # Создаем рецензию с реальным пользователем
    result = db_api.create_review(user_name, str(user_id), song_id, comment)
    
    return {
        "success": result,
        "user_id": user_id,
        "user_name": user_name
    }

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

@app.post("/auth/code")
async def auth_with_code(code: str = Body(..., embed=True)):
    result = db_api.verify_auth_code(code.upper())
    
    if not result or not result[0]:
        return {"success": False, "error": "Неверный или устаревший код"}
    
    user_tg_id, username = result
    
    # Получаем/создаем пользователя
    user_info = await db_api.user_in_db(user_tg_id)
    if not user_info:
        await db_api.create_user(username, user_tg_id)
        user_info = await db_api.user_in_db(user_tg_id)
    
    user_id = user_info[0] if user_info else None
    
    # Создаем сессионный токен
    session_token = secrets.token_urlsafe(32)
    
    return {
        "success": True,
        "token": session_token,
        "user": {
            "id": user_tg_id,
            "username": username,
            "user_id": user_id
        }
    }

@app.get("/auth/check/{user_tg_id}")
async def check_auth(user_tg_id: str):
    """Проверка авторизации пользователя"""
    user_info = await db_api.user_in_db(user_tg_id)
    if user_info:
        return {
            "authenticated": True,
            "user": {
                "id": user_info[0],
                "username": user_info[1],
                "tg_id": user_tg_id
            }
        }
    return {"authenticated": False}

@app.get("/auth/cleanup")
async def cleanup_auth_codes():
    """Очистка устаревших кодов (для планировщика)"""
    result = db_api.cleanup_expired_codes()
    return {"success": result}

# дл SimpleClient
@app.post("/create_auth_code")
async def api_create_auth_code(
    user_tg_id: str = Body(...),
    username: str = Body(...),
    code: str = Body(...),
    expires_minutes: int = Body(5)
):
    result = db_api.create_auth_code(user_tg_id, username, code, expires_minutes)
    return {"success": result}

@app.post("/verify_auth_code")
async def api_verify_auth_code(code: str = Body(...)):
    """API для проверки кода (для SimpleClient)"""
    result = db_api.verify_auth_code(code)
    if result and result[0]:
        return {"success": True, "user_tg_id": result[0], "username": result[1]}
    return {"success": False}

@app.get("/user_reviews/{user_tg_id}")
async def get_user_reviews_api(user_tg_id: str):
    """Получение всех рецензий пользователя"""
    # 1. Находим пользователя
    user_info = await db_api.user_in_db(user_tg_id)
    if not user_info:
        return {"success": False, "error": "User not found"}
    
    user_id = user_info[0]
    
    # 2. Получаем рецензии пользователя из БД
    conn = None
    try:
        import psycopg2
        from config import db_config
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Получаем ID всех рецензий пользователя
        sql = "SELECT user_review FROM users WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            return {"success": True, "reviews": []}
        
        review_ids = result[0]  # массив ID рецензий
        reviews = []
        
        # 3. Для каждой рецензии получаем детали
        for review_id in review_ids:
            sql = "SELECT review, review_author FROM review WHERE review_id = %s"
            cursor.execute(sql, (review_id,))
            review_data = cursor.fetchone()
            
            if review_data:
                review_text, author = review_data
                
                # Находим песню, к которой привязана рецензия
                sql = """
                SELECT name_song, author, song_id 
                FROM song 
                WHERE %s = ANY(review)
                """
                cursor.execute(sql, (review_id,))
                song_data = cursor.fetchone()
                
                song_name = song_data[0] if song_data else "Неизвестная песня"
                song_author = song_data[1] if song_data else "Неизвестен"
                song_id_val = song_data[2] if song_data else ""
                
                reviews.append({
                    "review_id": review_id,
                    "review_text": review_text,
                    "author": author,
                    "song_name": song_name,
                    "song_author": song_author,
                    "song_id": song_id_val
                })
        
        cursor.close()
        return {"success": True, "reviews": reviews}
        
    except Exception as e:
        print(f"Error getting user reviews: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if conn:
            conn.close()
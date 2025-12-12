import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

DB_API_URL = os.getenv("DB_API_URL", "http://db_api:8001")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # тут мы разрешаем запросы с любого домена, хотя можно было бы просто ввести мой локалхост
    allow_methods=["*"], # здесь методы HTTP запросов 
)

@app.get("/songs")
def get_songs():
    try:
        r = requests.get(f"{DB_API_URL}/songs", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        raise HTTPException(500, "DB API unavailable")

@app.get("/songs/{song_id}")
def get_song(song_id: str):
    try:
        r = requests.get(f"{DB_API_URL}/songs/{song_id}", timeout=5)
        if r.status_code == 404:
            raise HTTPException(404)
        r.raise_for_status()
        return r.json()
    except Exception:
        raise HTTPException(500, "DB API unavailable")

@app.post("/songs")
def create_song(name: str, author: str = None):
    try:
        r = requests.post(f"{DB_API_URL}/songs", params={"name": name, "author": author}, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        raise HTTPException(500, "DB API unavailable")

@app.post("/songs/{song_id}/reviews")
def add_review(song_id: str, review: str):
    try:
        r = requests.post(f"{DB_API_URL}/songs/{song_id}/reviews", params={"review": review}, timeout=5)
        if r.status_code == 404:
            raise HTTPException(404)
        r.raise_for_status()
        return r.json()
    except Exception:
        raise HTTPException(500, "DB API unavailable")

@app.get("/search")
def search(q: str, max_dist: int = 5, limit: int = 5):
    try:
        r = requests.get(f"{DB_API_URL}/search", params={"q": q, "max_dist": max_dist, "limit": limit}, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        raise HTTPException(500, "DB API unavailable")
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

DB_API_URL = os.getenv("DB_API_URL", "http://db_api:8001")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
)
#форматируем в json
def format_song(song_tuple):
    if not song_tuple or not isinstance(song_tuple, (list, tuple)):
        return None
    
    return {
        "song_id": song_tuple[0] if len(song_tuple) > 0 else None,
        "name_song": song_tuple[1] if len(song_tuple) > 1 else "",
        "author": song_tuple[2] if len(song_tuple) > 2 else None,
        "review": song_tuple[3] if len(song_tuple) > 3 else []
    }

def format_search_result(result_tuple):
    if not result_tuple or not isinstance(result_tuple, (list, tuple)):
        return None
    
    return {
        "song_id": result_tuple[0] if len(result_tuple) > 0 else None,
        "name_song": result_tuple[1] if len(result_tuple) > 1 else "",
        "author": result_tuple[2] if len(result_tuple) > 2 else None,
        "distance": result_tuple[-1] if result_tuple else 0
    }

# универсальный доступ
def make_api_request(method, endpoint, params=None, timeout=5):
    try:
        url = f"{DB_API_URL}{endpoint}"
        response = requests.request(method, url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            raise HTTPException(404, "Not found")
        raise HTTPException(500, "API error")
    except Exception:
        raise HTTPException(500, "API unavailable")


@app.get("/songs")
def get_songs():
    try:
        songs_tuples = make_api_request("GET", "/find_song", {"query": "", "type_search": "name"})
        return [format_song(song) for song in songs_tuples if format_song(song)]
    except HTTPException:
        raise HTTPException(404, "NO songs available")
        
@app.get("/songs/{song_id}")
def get_song(song_id: str):
    song_tuple = make_api_request("GET", f"/get_song/{song_id}")
    formatted = format_song(song_tuple)
    if not formatted:
        raise HTTPException(404, "Song not found")
    
    reviews_data = make_api_request("GET", f"/get_song_review/{song_id}")
    
    review_texts = []
    if reviews_data and isinstance(reviews_data, list):
        for review_tuple in reviews_data:
            if len(review_tuple) > 2:  
                review_texts.append(f"{review_tuple[1]}: {review_tuple[2]}")
    
    formatted["review"] = review_texts
    
    return formatted

@app.post("/songs")
def create_song(name: str, author: str = None):
    result = make_api_request("POST", "/create_web_song", {"name_song": name, "author": author}, timeout=10)
    
    return {
        "success": True,
        "song_id": result if isinstance(result, int) else None,  
        "message": "Песня добавлена успешно!", 
        "name": name, 
        "author": author or "нет автора"
    }

@app.post("/songs/{song_id}/reviews")
def add_review(song_id: str, review: str, author_name: str = "Anonymous"):
    result = make_api_request("POST", "/create_web_review", {
        "user_name": author_name,
        "user_id": 999,
        "song_id": song_id,
        "comment": review
    })
    
    return {
        "success": result if isinstance(result, bool) else True,
        "message": "Рецензия добавлена успешно!", 
        "song_id": song_id,
        "author": author_name
    }


@app.get("/search")
def search(q: str, max_dist: int = 5, limit: int = 5, type_search: str = "name"):
    results_tuples = make_api_request("GET", "/find_song", {"query": q, "type_search": type_search})
    return [format_search_result(result) for result in results_tuples[:limit] if format_search_result(result)]
from fastapi import FastAPI, HTTPException
from db_api import db_api

app = FastAPI()

@app.get("/songs")
def get_all_songs():
    songs = db_api.get_all_song()
    if songs is None:
        return []
    return [dict(song) for song in songs]

@app.get("/songs/{song_id}")
def get_song(song_id: str):
    song = db_api.get_song(song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return dict(song)

@app.post("/songs")
def add_song(name: str, author: str = None):
    success = db_api.create_song(name, author)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create song")
    return {"status": "created"}

@app.post("/songs/{song_id}/reviews")
def add_review(song_id: str, review: str):
    success = db_api.create_review(song_id, review)
    if not success:
        raise HTTPException(status_code=404, detail="Song not found or failed to add review")
    return {"status": "review added"}

@app.get("/search")
def search(q: str, max_dist: int = 5, limit: int = 5, type_search: str = "NAME"):
    from db_api import db_api
    
    if type_search.upper() == "AUTHOR":
        search_type = db_api.FindBy.AUTHOR
    else:
        search_type = db_api.FindBy.NAME
        
    results = db_api.find_song(q, max_dist, limit, search_type)
    if results is None:
        return []
    return [dict(r) for r in results]
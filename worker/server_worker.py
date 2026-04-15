from fastapi import FastAPI, Form, Body
import uvicorn
from worker import ProfanityChecker
from typing import Optional
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY")
detector = ProfanityChecker(API_KEY)


@app.post("/check")
async def check_text(
        text: Optional[str] = Body(None, embed=True),  # Для JSON: {"text": "..."}
        text_query: Optional[str] = None  # Для ?text=...
):
    input_text = text or text_query

    if not input_text:
        return {"error": "Текст не предоставлен"}

    result = detector.check_text(input_text)
    return result["has_profanity"]


@app.get("/")
def home():
    return {
        "message": "Profanity Detection API",
        "try_it": "Отправьте POST запрос на /check",
        "examples": {
            "curl_json": 'curl -X POST http://localhost:8000/check -H "Content-Type: application/json" -d \'{"text": "Привет"}\'',
            "curl_form": 'curl -X POST http://localhost:8000/check -d "text=Привет"',
            "curl_query": 'curl -X POST "http://localhost:8000/check?text=Привет"'
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
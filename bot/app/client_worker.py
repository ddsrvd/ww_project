import requests
import os

WORKER_URL = os.getenv("WORKER_URL")
def check_text(text: str) -> bool:
    try:
        response = requests.post(f"{WORKER_URL}/check", json={"text": text}, timeout=10)

        # Проверяем статус
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка {response.status_code}")
            print(f"Ответ сервера: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        print("Сервер не запущен.")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

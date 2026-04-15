import requests
import json


class ProfanityChecker:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def check_text(self, text):
        print(f"Проверяем: '{text[:30]}'")

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-v3.2",
                    "messages": [
                        {
                            "role": "system",
                            "content": """Ты детектор нецензурной лексики. 
                            Отвечай строго в формате JSON:
                            {"has_profanity": true/false, "confidence": 0-1, 
                             "reason": "объяснение", "found_words": []}"""
                        },
                        {
                            "role": "user",
                            "content": f"Проанализируй текст: '{text}'"
                        }
                    ]
                },
                timeout=15
            )

            response.raise_for_status()  # Проверяем на ошибки HTTP

            data = response.json()
            ai_response = data["choices"][0]["message"]["content"]

            try:
                start = ai_response.find('{')
                end = ai_response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = ai_response[start:end]
                    result = json.loads(json_str)
                else:
                    has_profanity = any(
                        word in ai_response.lower() for word in ['мат', 'оскорблен', 'брань', 'ругательств'])
                    result = {
                        "has_profanity": has_profanity,
                        "confidence": 0.8 if has_profanity else 0.2,
                        "reason": ai_response,
                        "found_words": []
                    }
            except json.JSONDecodeError:
                result = {
                    "has_profanity": False,
                    "confidence": 0,
                    "reason": f"Ошибка парсинга: {ai_response[:50]}",
                    "found_words": []
                }

            return {
                "text": text,
                **result,
                "raw_response": ai_response[:100] + "..." if len(ai_response) > 100 else ai_response
            }

        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return {
                "text": text,
                "has_profanity": False,
                "confidence": 0,
                "reason": f"Ошибка сети: {str(e)}",
                "found_words": [],
                "error": True
            }
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return {
                "text": text,
                "has_profanity": False,
                "confidence": 0,
                "reason": f"Ошибка: {str(e)}",
                "found_words": [],
                "error": True
            }

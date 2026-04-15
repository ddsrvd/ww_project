FROM python:3.11

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы
COPY . .

# Запускаем сервер
CMD ["python", "server_worker.py"]
import asyncio
import logging #удалить

from config import TOKEN
from app.hand import router

from aiogram import Bot, Dispatcher

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) #Удалить потом
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

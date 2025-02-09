from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import handlers
import asyncio

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(handlers.rt)

async def bot_run():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(bot_run())

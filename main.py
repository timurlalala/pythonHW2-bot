from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import set_profile_handlers, usage_handlers
import asyncio

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_routers(set_profile_handlers.rt, usage_handlers.rt)

async def bot_run():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(bot_run())

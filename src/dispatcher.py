from settings import BOT_TOKEN
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers.handlers import handlers_router
from admin_handlers.admin_handlers import admin_handlers_router


TOKEN = BOT_TOKEN

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp.include_router(handlers_router)
dp.include_router(admin_handlers_router)


async def start_polling():
    print("Polling has started")
    await dp.start_polling(bot)
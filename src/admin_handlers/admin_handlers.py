from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from services.handlers_services import get_master
from services.admin_services import get_message_from_schedules, get_message_from_photos
from static_text.static_text import ADMIN_NO_PHOTO_TEXT
import logging


admin_handlers_router = Router()


@admin_handlers_router.message(F.text == "Расписание на сегодня")
async def get_schedule_for_today(message: Message) -> None:
    logging.info(f"Schedule for today from {message.chat.id}")
    user = await get_master(message.chat.id)
    department = user.department
    text = await get_message_from_schedules(department)
    await message.reply(text)


@admin_handlers_router.message(F.text == "Фото рабочего места")
async def get_photos_for_today(message: Message) -> None:
    logging.info(f"Photos for today from {message.chat.id}")
    user = await get_master(message.chat.id)
    department = user.department
    results = await get_message_from_photos(department)
    if not results:
        await message.reply(ADMIN_NO_PHOTO_TEXT)
        return
    for result in results:
        photo = FSInputFile(result["image_link"])
        text = result["text"]
        await message.reply_photo(photo=photo, caption=text)
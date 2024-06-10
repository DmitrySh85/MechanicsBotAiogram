from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from services.handlers_services import get_master
from services.admin_services import get_message_from_schedules, get_message_from_photos


admin_handlers_router = Router()


@admin_handlers_router.message(F.text == "Расписание на сегодня")
async def get_schedule_for_today(message: Message) -> None:
    user = await get_master(message.chat.id)
    department = user.department
    text = await get_message_from_schedules(department)
    await message.reply(text)


@admin_handlers_router.message(F.text == "Фото рабочего места")
async def get_photos_for_today(message: Message) -> None:
    user = await get_master(message.chat.id)
    department = user.department
    results = await get_message_from_photos(department)
    for result in results:
        photo = FSInputFile(result["image_link"])
        text = result["text"]
        await message.reply_photo(photo=photo, caption=text)
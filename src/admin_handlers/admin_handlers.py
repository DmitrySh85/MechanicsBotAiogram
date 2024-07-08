from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from services.handlers_services import get_master
from services.admin_services import (
    get_message_from_schedules,
    get_message_from_photos,
    parse_date_from_message_text,
    get_images_and_messages_for_the_date
)
from static_text.static_text import (
    ADMIN_NO_PHOTO_TEXT,
    USER_IS_NOT_MANAGER,
    DATE_SELECT_TEXT,
    DATE_ERROR_TEXT
)
import logging
from forms.forms import DateSelectState
from keyboards.keyboards import admin_keyboard


admin_handlers_router = Router()


@admin_handlers_router.message(F.text == "Расписание на сегодня")
async def get_schedule_for_today(message: Message) -> None:
    logging.info(f"Schedule for today from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user or not user.is_manager:
        return await message.reply(USER_IS_NOT_MANAGER)
    department = user.department
    text = await get_message_from_schedules(department)
    await message.reply(text)


@admin_handlers_router.message(F.text == "Фото рабочего места")
async def get_photos_for_today(message: Message) -> None:
    logging.info(f"Photos for today from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user or not user.is_manager:
        return await message.reply(USER_IS_NOT_MANAGER)
    department = user.department
    results = await get_message_from_photos(department)
    if not results:
        return await message.reply(ADMIN_NO_PHOTO_TEXT)
    for result in results:
        photo = FSInputFile(result["image_link"])
        text = result["text"]
        await message.reply_photo(photo=photo, caption=text, reply_markup=admin_keyboard)


@admin_handlers_router.message(F.text == "Фото за выбранный день")
async def send_date_request(message: Message, state: FSMContext) -> None:
    logging.info(f"Photos for the day from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user or not user.is_manager:
        return await message.reply(USER_IS_NOT_MANAGER)
    await message.reply(DATE_SELECT_TEXT)
    await state.set_state(DateSelectState.date_select)


@admin_handlers_router.message(DateSelectState.date_select)
async def get_photos_for_the_date(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        date = parse_date_from_message_text(message.text)
    except ValueError as e:
        logging.error(e)
        return await message.reply(DATE_ERROR_TEXT, reply_markup=admin_keyboard)
    results = await get_images_and_messages_for_the_date(date)
    if not results:
        return await message.reply(ADMIN_NO_PHOTO_TEXT)
    for result in results:
        photo = FSInputFile(result["image_link"])
        text = result["text"]
        await message.reply_photo(photo=photo, caption=text, reply_markup=admin_keyboard)


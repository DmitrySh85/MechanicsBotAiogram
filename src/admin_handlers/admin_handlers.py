from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from services.handlers_services import get_master
from services.admin_services import (
    get_message_from_schedules,
    get_message_from_photos,
    parse_date_from_message_text,
    get_images_and_messages_for_the_date,
    get_discipline_violation_text
)
from static_text.static_text import (
    ADMIN_NO_PHOTO_TEXT,
    USER_IS_NOT_MANAGER,
    DATE_SELECT_TEXT,
    DATE_ERROR_TEXT,
    DISCIPLINE_VIOLATION_BTN
)
import logging
from forms.forms import DateSelectState
from keyboards.keyboards import admin_keyboard
from services.users_services import update_username


admin_handlers_router = Router()


@admin_handlers_router.message(F.text == "Расписание на сегодня")
async def get_schedule_for_today(message: Message) -> None:
    logging.info(f"Schedule for today from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user or not user.is_manager:
        await message.reply(USER_IS_NOT_MANAGER)
        return
    username = message.from_user.full_name
    user_id = user.id
    await update_username(user_id, username)
    department = user.department
    text = await get_message_from_schedules(department)
    await message.reply(text)


@admin_handlers_router.message(F.text == "Фото рабочего места")
async def get_photos_for_today(message: Message) -> None:
    logging.info(f"Photos for today from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user or not user.is_manager:
        await message.reply(USER_IS_NOT_MANAGER)
        return
    department = user.department
    results = await get_message_from_photos(department)
    user_id = user.id
    username = message.from_user.full_name
    await update_username(user_id, username)
    if not results:
        await message.reply(ADMIN_NO_PHOTO_TEXT)
        return
    for result in results:
        photo = FSInputFile(result["image_link"])
        text = result["text"]
        await message.reply_photo(photo=photo, caption=text, reply_markup=admin_keyboard)


@admin_handlers_router.message(F.text == "Фото за выбранный день")
async def send_date_request(message: Message, state: FSMContext) -> None:
    logging.info(f"Photos for the day from {message.chat.id}")
    user = await get_master(message.chat.id)
    user_id = user.id
    username = message.from_user.full_name
    await update_username(user_id, username)
    if not user or not user.is_manager:
        await message.reply(USER_IS_NOT_MANAGER)
        return
    await message.reply(DATE_SELECT_TEXT)
    await state.set_state(DateSelectState.date_select)


@admin_handlers_router.message(DateSelectState.date_select)
async def get_photos_for_the_date(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        date = parse_date_from_message_text(message.text)
    except ValueError as e:
        logging.error(e)
        await message.reply(DATE_ERROR_TEXT, reply_markup=admin_keyboard)
        return
    results = await get_images_and_messages_for_the_date(date)
    if not results:
        await message.reply(ADMIN_NO_PHOTO_TEXT)
        return
    for result in results:
        photo = FSInputFile(result["image_link"])
        text = result["text"]
        await message.reply_photo(photo=photo, caption=text, reply_markup=admin_keyboard)


@admin_handlers_router.message(F.text == DISCIPLINE_VIOLATION_BTN)
async def get_discipline_violation(message: Message) -> None:
    logging.info(f"get discipline violation from {message.chat.id}")
    user = await get_master(message.chat.id)
    user_id = user.id
    username = message.from_user.full_name
    await update_username(user_id, username)
    if not user or not user.is_manager:
        await message.reply(USER_IS_NOT_MANAGER)
        return
    text = await get_discipline_violation_text()
    chunk_size = 4096
    messages_texts = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    for message_text in messages_texts:
        m = await message.reply(text=message_text)
        await m.bot.edit_message_reply_markup(
            message_id=m.message_id,
            chat_id=message.chat.id,
            reply_markup=admin_keyboard,
        )

    await message.answer(message_text, reply_markup=admin_keyboard)


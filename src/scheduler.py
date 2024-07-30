from dispatcher import bot
from services.schedule_services import (
    check_masters_not_send_photo,
    check_master_names_not_send_photo
)
import pytz
import logging
from datetime import datetime, timedelta
from static_text.static_text import MISSING_PHOTO_TEXT, NO_PHOTO_ADMIN_NOTIFICATION_TEXT
from keyboards.keyboards import master_keyboard, admin_keyboard
from services.users_services import get_manager_tg_ids_from_db


async def send_reminder_to_masters():
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    start_time = now - timedelta(minutes=30)
    masters_tg_ids = await check_masters_not_send_photo(start_time, now)
    logging.info(f"Не прислали фото: {masters_tg_ids}")
    for tg_id in masters_tg_ids:
        await bot.send_message(tg_id.tg_id, MISSING_PHOTO_TEXT, reply_markup=master_keyboard)


async def send_reminder_to_admins():
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    start_time = now - timedelta(minutes=45)
    masters = await check_master_names_not_send_photo(start_time, now)
    if not masters:
        return
    master_names = ", ".join([master.name for master in masters]).strip()
    logging.info(f"Не прислали фото: {master_names}")
    managers_chat_ids = await get_manager_tg_ids_from_db()
    message_text = NO_PHOTO_ADMIN_NOTIFICATION_TEXT.format(masters=master_names)
    for chat_id in managers_chat_ids:
        await bot.send_message(chat_id, message_text, reply_markup=admin_keyboard)






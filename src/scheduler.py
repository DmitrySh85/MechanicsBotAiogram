import asyncio

from dispatcher import bot
from services.schedule_services import (
    check_masters_not_send_photo,
    check_master_names_not_send_photo,
    get_monthly_report_text,
)
import pytz
import logging
from datetime import datetime, timedelta
from static_text.static_text import (
    MISSING_PHOTO_TEXT,
    NO_PHOTO_ADMIN_NOTIFICATION_TEXT,
    GENERAL_CLEANING_REMINDER_TEXT
)
from keyboards.keyboards import master_keyboard, admin_keyboard
from services.users_services import get_manager_tg_ids_from_db
from services.discipline_violation_services import create_discipline_violation
from services.general_cleaning_services import get_general_cleaning
from services.general_cleaning_reaction_services import (
    get_general_cleaning_reactions,
    process_reactions_to_text
)
from senders.senders import (
    send_general_cleaning_message,
    send_tomorrow_general_cleaning_message,
    send_two_day_general_cleaning_reminder_message,
    send_reactions_to_admin
)


async def send_day_reminder_to_masters():
    logging.info("send_reminder_to_masters")
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    start_time = now - timedelta(minutes=2400)
    category = "Начало рабочего дня"
    masters_tg_ids = await check_masters_not_send_photo(start_time, now, category)
    logging.info(f"Не прислали фото: {masters_tg_ids}")
    for tg_id in masters_tg_ids:
        try:
            await bot.send_message(tg_id.tg_id, MISSING_PHOTO_TEXT, reply_markup=master_keyboard)
        except Exception as e:
            logging.warning(e)


async def send_evening_reminder_to_masters():
    logging.info("send_reminder_to_masters")
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    start_time = now - timedelta(minutes=240)
    category = "Завершение рабочего дня"
    masters_tg_ids = await check_masters_not_send_photo(start_time, now, category)
    logging.info(f"Не прислали фото: {masters_tg_ids}")
    for tg_id in masters_tg_ids:
        try:
            await bot.send_message(tg_id.tg_id, MISSING_PHOTO_TEXT, reply_markup=master_keyboard)
        except Exception as e:
            logging.warning(e)


async def send_day_reminder_to_admins():
    logging.info("send_reminder_to_admins")
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    start_time = now - timedelta(hours=3, minutes=45)
    masters = await check_master_names_not_send_photo(start_time, now)
    if not masters:
        return
    master_names = ", ".join([master.name for master in masters]).strip()
    logging.info(f"Не прислали фото: {master_names}")
    managers_chat_ids = await get_manager_tg_ids_from_db()
    message_text = NO_PHOTO_ADMIN_NOTIFICATION_TEXT.format(masters=master_names)
    for chat_id in managers_chat_ids:
        await bot.send_message(chat_id, message_text, reply_markup=admin_keyboard)


async def send_evening_reminder_to_admins():
    logging.info("send_reminder_to_admins")
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    start_time = now - timedelta(hours=5, minutes=45)
    masters = await check_master_names_not_send_photo(start_time, now)
    if not masters:
        return
    master_names = ", ".join([master.name for master in masters]).strip()
    logging.info(f"Не прислали фото: {master_names}")
    managers_chat_ids = await get_manager_tg_ids_from_db()
    message_text = NO_PHOTO_ADMIN_NOTIFICATION_TEXT.format(masters=master_names)
    for chat_id in managers_chat_ids:
        await bot.send_message(chat_id, message_text, reply_markup=admin_keyboard)


async def save_discipline_violation():
    logging.info("save discipline violation")
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz)
    start_time = now - timedelta(minutes=45)
    masters = await check_master_names_not_send_photo(start_time, now)
    if not masters:
        return
    for master in masters:
        await create_discipline_violation(master.id)


async def get_monthly_report():
    logging.info("Get monthly report")
    message_text = await get_monthly_report_text()
    managers_chat_ids = await get_manager_tg_ids_from_db()
    for chat_id in managers_chat_ids:
        await bot.send_message(chat_id, message_text, reply_markup=admin_keyboard)


async def check_two_day_left_before_general_cleaning_and_send_message():
    logging.info("check two days left before general cleaning scheduled")
    two_days = tomorrow = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=2)
    general_cleaning = await get_general_cleaning(tomorrow)
    if not general_cleaning:
        return
    general_cleaning_id = general_cleaning.id
    await send_two_day_general_cleaning_reminder_message(bot, two_days, general_cleaning_id)
    sleep_time = 3600
    await asyncio.sleep(sleep_time)
    reactions = await get_general_cleaning_reactions(general_cleaning_id)
    message_text = process_reactions_to_text(reactions)
    await send_reactions_to_admin(bot, message_text)


async def check_one_day_left_before_general_cleaning_and_send_message():
    logging.info("check tommorow is general cleaning scheduled")
    tomorrow = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    general_cleaning = await get_general_cleaning(tomorrow)
    if general_cleaning:
        await send_tomorrow_general_cleaning_message(bot, tomorrow)


async def check_general_cleaning_and_send_messages():
    logging.info("Check general cleaning")
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    general_cleaning = await get_general_cleaning(today)
    if general_cleaning:
        await send_general_cleaning_message(bot, today)


async def remind_to_admin_about_general_cleaning():
    logging.info("remind_to_admin_about_general_cleaning")
    message_text = GENERAL_CLEANING_REMINDER_TEXT
    managers_chat_ids = await get_manager_tg_ids_from_db()
    for chat_id in managers_chat_ids:
        await bot.send_message(chat_id, message_text, reply_markup=admin_keyboard)


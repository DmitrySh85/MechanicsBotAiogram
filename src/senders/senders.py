import datetime
import logging

from aiogram import Bot
from aiogram.enums import ParseMode

from aiogram.types import Message
from static_text.static_text import (
    NO_USER_FOUND_TEXT,
    REGISTRATION_REQUEST_MESSAGE,
    GENERAL_CLEANING_SCHEDULED_MESSAGE,
    GENERAL_CLEANING_TOMORROW_MESSAGE,
    GENERAL_CLEANING_TWO_DAYS_LEFT_MESSAGE
)

from keyboards.keyboards import (
    confirm_registration_kb,
    general_cleaning_start_kb,
    general_cleaning_accept_kb,
    admin_keyboard
)
from services.users_services import get_manager_tg_ids_from_db

from services.admin_services import (
    get_available_and_not_day_off_masters,
    get_working_masters_tg_ids
)



async def send_not_registered_message(message: Message):
    return await message.answer(NO_USER_FOUND_TEXT)


async def send_registration_request_to_admin(message: Message):

    managers_chat_ids = await get_manager_tg_ids_from_db()
    for manager_id in managers_chat_ids:
        await message.bot.send_message(
            chat_id=manager_id,
            text=REGISTRATION_REQUEST_MESSAGE.format(
                user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            ),  # type: ignore
            reply_markup=confirm_registration_kb(message.from_user),
        )


async def send_general_cleaning_message(
        bot: Bot,
        date: datetime.date
) -> None:
    masters_chats_ids = await get_available_and_not_day_off_masters(date)
    for master_chat_id in masters_chats_ids:
        try:
            await bot.send_message(
                chat_id=master_chat_id,
                text=GENERAL_CLEANING_SCHEDULED_MESSAGE.format(date=date.strftime("%d-%m-%Y")),
                reply_markup=general_cleaning_start_kb()
            )
        except Exception as e:
            logging.debug(e)
            continue


async def send_tomorrow_general_cleaning_message(
        bot: Bot,
        date: datetime.date
) -> None:
    masters_chats_ids = await get_working_masters_tg_ids()
    for master_chat_id in masters_chats_ids:
        try:
            await bot.send_message(
                chat_id=master_chat_id,
                text=GENERAL_CLEANING_TOMORROW_MESSAGE.format(date=date.strftime("%d-%m-%Y")),
            )
        except Exception as e:
            logging.debug(e)
            continue


async def send_two_day_general_cleaning_reminder_message(
        bot: Bot,
        date: datetime.date,
        general_cleaning_id: int
) -> None:
    masters_chats_ids = await get_working_masters_tg_ids()
    for master_chat_id in masters_chats_ids:
        try:
            await bot.send_message(
                chat_id=master_chat_id,
                text=GENERAL_CLEANING_TWO_DAYS_LEFT_MESSAGE.format(date=date.strftime("%d-%m-%Y")),
                reply_markup=general_cleaning_accept_kb(general_cleaning_id)
            )
        except Exception as e:
            logging.debug(e)
            continue


async def send_reactions_to_admin(
        bot: Bot,
        text: str
) -> None:
    MAX_MESSAGE_LENGTH = 4096
    managers_chat_ids = await get_manager_tg_ids_from_db()

    for manager_id in managers_chat_ids:
        for part in split_text(text, MAX_MESSAGE_LENGTH):
            await bot.send_message(
                chat_id=manager_id,
                text=part,
                reply_markup=admin_keyboard,
                parse_mode=ParseMode.MARKDOWN_V2
            )


def split_text(text, max_length):

    for i in range(0, len(text), max_length):
        yield text[i:i + max_length]
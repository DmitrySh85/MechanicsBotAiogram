from aiogram.types import Message
from static_text.static_text import (
    NO_USER_FOUND_TEXT,
    REGISTRATION_REQUEST_MESSAGE,
)

from keyboards.keyboards import confirm_registration_kb
from services.users_services import get_manager_tg_ids_from_db


async def send_not_registered_message(message: Message):
    return await message.answer(NO_USER_FOUND_TEXT)


async def send_registration_request_to_admin(message: Message):

    managers_chat_ids = await get_manager_tg_ids_from_db()
    for manager_id in managers_chat_ids:
        await message.bot.send_message(
                chat_id=manager_id,
                text=REGISTRATION_REQUEST_MESSAGE.format(user_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name, last_name=message.from_user.last_name),  # type: ignore
                reply_markup=confirm_registration_kb(message.from_user),
                )
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
import logging


async def delete_callback_query_message(
        callback_query: CallbackQuery,
        message_id: int,
):
    try:
        await callback_query.message.bot.delete_message(message_id=message_id, chat_id=callback_query.message.chat.id)
    except TelegramBadRequest as e:
        logging.debug(e)


async def delete_message(
        message: Message,
        message_id: int
):
    try:
        await message.bot.delete_message(message_id=message_id, chat_id=message.chat.id)
    except TelegramBadRequest as e:
        logging.debug(e)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import html, Router, F
from static_text.static_text import (
    ADMIN_START_TEXT,
    MASTER_START_TEXT,
    MASTER_START_WORK_TEXT,
    MASTER_END_WORK_TEXT,
    MASTER_START_WORK_IMAGE_RECEIVED_TEXT,
    MASTER_END_WORK_IMAGE_RECEIVED_TEXT,
    NO_MASTER_FOUND,
    registration_confirm_callback_data,
    registration_reject_callback_data,
    REGISTRATION_REJECT_MESSAGE

)
from services.handlers_services import (
    get_master,
    save_image,
    create_master_and_schedule
    )
from keyboards.keyboards import master_keyboard, admin_keyboard
from forms.forms import StartWorkForm, EndWorkForm
import logging
from senders.senders import (
    send_not_registered_message,
    send_registration_request_to_admin
)
from services.users_services import (
    register_user,
    reject_user
)

handlers_router = Router()


@handlers_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    logging.info(f"Start command from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user:
        await send_registration_request_to_admin(message)
        await send_not_registered_message(message)

    if user.is_manager:
        await message.answer(f"Добрый день, {html.bold(message.from_user.full_name)}!\n{ADMIN_START_TEXT}",
                             reply_markup=admin_keyboard)
        return
    await message.answer(f"Добрый день, {html.bold(message.from_user.full_name)}!\n{MASTER_START_TEXT}",
                         reply_markup=master_keyboard)


@handlers_router.callback_query(
    F.data.startswith(registration_confirm_callback_data)
)
async def handle_register_confirmation(callback_query: CallbackQuery):
    try:
        user_id = int(callback_query.data.split(":")[1])
        username = callback_query.data.split(":")[2]
    except IndexError:
        logging.error("Invalid data format")
        return
    except Exception as e:
        logging.error(e)
        return
    try:
        await register_user(user_id, username)
        await callback_query.answer(f"User {user_id} has been registered.")
    except ValueError:
        return await callback_query.answer(f"User {user_id} already has been registered.")

    await callback_query.message.edit_text(
        f"User {user_id} has been registered.", reply_markup=None
    )
    await callback_query.bot.send_message(chat_id=user_id, text=MASTER_START_TEXT, reply_markup=master_keyboard)


@handlers_router.callback_query(
    F.data.startswith(registration_reject_callback_data)
)
async def handle_register_rejection(callback_query: CallbackQuery):
    try:
        user_id = int(callback_query.data.split(":")[1])
        username = callback_query.data.split(":")[2]
    except IndexError:
        logging.error("Invalid data format")
        return
    except Exception as e:
        logging.error(e)
        return
    await reject_user(user_id, username)
    await callback_query.answer(f"User {user_id} has been rejected.")
    await callback_query.message.edit_text(
        f"User {user_id} {username} has been blocked.", reply_markup=None
    )
    await callback_query.bot.send_message(
        chat_id=user_id, text=REGISTRATION_REJECT_MESSAGE
    )

@handlers_router.message(Command("chat"))
async def send_telegram_id(message: Message) -> None:
    logging.info(f"Chat id request from {message.chat.id}")
    await message.answer(f"Ваш id в телеграм {message.chat.id}.")


@handlers_router.message(F.text == "Приступил к работе")
async def start_work_handler(message: Message, state: FSMContext) -> None:
    logging.info(f"Start work button from {message.chat.id}")
    await state.set_state(StartWorkForm.start_work)
    await message.answer(MASTER_START_WORK_TEXT, reply_markup=master_keyboard)


@handlers_router.message(StartWorkForm.start_work, F.photo)
async def process_start_work_image(message: Message, state: FSMContext) -> None:
    logging.info(f"Start work image from {message.chat.id}")
    await save_image(message)
    await state.clear()
    await message.answer(MASTER_START_WORK_IMAGE_RECEIVED_TEXT, reply_markup=master_keyboard)


@handlers_router.message(F.text == "Закончил работу")
async def end_work_handler(message: Message, state: FSMContext) -> None:
    logging.info(f"End work button from {message.chat.id}")
    await state.set_state(EndWorkForm.end_work)
    await message.answer(MASTER_END_WORK_TEXT, reply_markup=master_keyboard)


@handlers_router.message(EndWorkForm.end_work, F.photo)
async def process_start_work_image(message: Message, state: FSMContext) -> None:
    logging.info(f"End work image from {message.chat.id}")
    await save_image(message)
    await state.clear()
    await message.answer(MASTER_END_WORK_IMAGE_RECEIVED_TEXT, reply_markup=master_keyboard)




from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import html, Router, F
from static_text.static_text import (
    ADMIN_START_TEXT,
    MASTER_START_TEXT,
    MASTER_START_WORK_TEXT,
    MASTER_END_WORK_TEXT,
    MASTER_START_WORK_IMAGE_RECEIVED_TEXT,
    MASTER_END_WORK_IMAGE_RECEIVED_TEXT,
    NO_MASTER_FOUND
)
from services.handlers_services import (
    get_master,
    save_image,
    create_master_and_schedule
    )
from keyboards.keyboards import master_keyboard, admin_keyboard
from forms.forms import StartWorkForm, EndWorkForm


handlers_router = Router()


@handlers_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user = await get_master(message.chat.id)
    if not user:
        await create_master_and_schedule(message)
        await message.answer(f"Добрый день, {html.bold(message.from_user.full_name)}!\n{MASTER_START_TEXT}",
                             reply_markup=master_keyboard)
        return
    if user.is_manager:
        await message.answer(f"Добрый день, {html.bold(message.from_user.full_name)}!\n{ADMIN_START_TEXT}",
                             reply_markup=admin_keyboard)
        return
    await message.answer(f"Добрый день, {html.bold(message.from_user.full_name)}!\n{MASTER_START_TEXT}",
                         reply_markup=master_keyboard)


@handlers_router.message(Command("chat"))
async def send_telegram_id(message: Message) -> None:
    await message.answer(f"Ваш id в телеграм {message.chat.id}.")


@handlers_router.message(F.text == "Приступил к работе")
async def start_work_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(StartWorkForm.start_work)
    await message.answer(MASTER_START_WORK_TEXT, reply_markup=master_keyboard)


@handlers_router.message(StartWorkForm.start_work, F.photo)
async def process_start_work_image(message: Message, state: FSMContext) -> None:
    await save_image(message)
    await state.clear()
    await message.answer(MASTER_START_WORK_IMAGE_RECEIVED_TEXT, reply_markup=master_keyboard)


@handlers_router.message(F.text == "Закончил работу")
async def end_work_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(EndWorkForm.end_work)
    await message.answer(MASTER_END_WORK_TEXT, reply_markup=master_keyboard)


@handlers_router.message(EndWorkForm.end_work, F.photo)
async def process_start_work_image(message: Message, state: FSMContext) -> None:
    await save_image(message)
    await state.clear()
    await message.answer(MASTER_END_WORK_IMAGE_RECEIVED_TEXT, reply_markup=master_keyboard)




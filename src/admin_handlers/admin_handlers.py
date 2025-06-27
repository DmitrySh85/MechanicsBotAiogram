from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from services.handlers_services import get_master
from services.telegram_services import delete_callback_query_message
from services.admin_services import (
    get_message_from_schedules,
    get_message_from_photos,
    parse_date_from_message_text,
    get_images_and_messages_for_the_date,
    get_discipline_violation_text,
    get_available_masters,
    delete_selected_masters,
    get_working_masters_chats_ids
)
from static_text.static_text import (
    ADMIN_NO_PHOTO_TEXT,
    USER_IS_NOT_MANAGER,
    DATE_SELECT_TEXT,
    DATE_ERROR_TEXT,
    DISCIPLINE_VIOLATION_BTN,
    DELETE_MASTERS,
    MASTER_DELETE_CHOOSE_TEXT,
    MASTERS_SELECT_CANCELLED_TEXT,
    GENERAL_CLEANING_BTN,
    GENERAL_CLEANING
)
import logging
from forms.forms import DateSelectState, MastersSelectState
from keyboards.keyboards import (
    admin_keyboard,
    master_choose_keyboard,
    general_cleaning_start_kb
)
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


@admin_handlers_router.message(F.text == DELETE_MASTERS)
async def delete_worekers(message: Message, state: FSMContext) -> None:
    logging.info(f"Assign workers for today")
    available_masters = await get_available_masters()

    await state.update_data(
        available_masters=available_masters,
        selected_masters_names=list([]),
        selected_masters_ids=list([]),
    )
    await state.set_state(MastersSelectState.master_select)

    message_text = MASTER_DELETE_CHOOSE_TEXT
    response = await message.reply(
        message_text,
        reply_markup=master_choose_keyboard(available_masters)
    )
    message_id = response.message_id
    chat_id = message.chat.id
    await state.update_data(message_id=message_id, chat_id=chat_id)


@admin_handlers_router.callback_query(MastersSelectState.master_select, F.data == "cancel_mchs")
async def cancel_masters_choose(callback_query: CallbackQuery, state: FSMContext) -> None:
    logging.info(f"Cancelled masters for today")

    data = await state.get_data()
    message_id = data["message_id"]
    await delete_callback_query_message(callback_query, message_id)

    await state.clear()
    await callback_query.answer()
    await callback_query.message.answer(MASTERS_SELECT_CANCELLED_TEXT)


@admin_handlers_router.callback_query(MastersSelectState.master_select, F.data.startswith("mchs"))
async def choose_master(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    master_id = int(callback_query.data.split(":")[1])
    available_masters = data["available_masters"]
    selected_masters_names = data["selected_masters_names"]
    selected_masters_ids = data["selected_masters_ids"]
    master_name = available_masters.pop(master_id)
    selected_masters_ids.append(master_id)
    selected_masters_names.append(master_name)

    message_id = data["message_id"]
    await delete_callback_query_message(callback_query, message_id)

    message_text = "Выбран(ы) мастер(а)" + "\n" + "\n".join([selected_master_name for selected_master_name in selected_masters_names])

    await callback_query.answer()
    response = await callback_query.message.answer(
        message_text,
        reply_markup=master_choose_keyboard(available_masters)
    )
    await state.update_data(message_id=response.message_id)


@admin_handlers_router.callback_query(MastersSelectState.master_select, F.data == "finish_mchs")
async def finish_master_choose(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    selected_masters_names = data["selected_masters_names"]
    selected_masters_ids = data["selected_masters_ids"]
    await delete_selected_masters(selected_masters_ids)

    message_id = data["message_id"]
    await delete_callback_query_message(callback_query, message_id)

    await callback_query.answer()
    await state.clear()

    message_text = "Удалены мастера:\n" + "\n".join(selected_masters_names)
    await callback_query.message.answer(
        message_text
    )


@admin_handlers_router.message(F.text == GENERAL_CLEANING_BTN)
async def init_general_cleaning(message: Message, state: FSMContext) -> None:
    masters_chats_ids = await get_working_masters_chats_ids()
    for master in masters_chats_ids:
        try:
            await message.bot.send_message(
                text=GENERAL_CLEANING,
                chat_id=master,
                reply_markup=general_cleaning_start_kb()
            )
        except TelegramBadRequest as e:
            logging.debug(f"{e}: {master}")
            continue
    await message.reply(
        "Генеральная уборка назначена на сегодня."
    )

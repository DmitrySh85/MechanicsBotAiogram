from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from services.handlers_services import (
    get_master,
    convert_master_data_to_text
)
from services.telegram_services import delete_callback_query_message
from services.admin_services import (
    get_message_from_schedules,
    get_message_from_photos,
    parse_date_from_message_text,
    get_images_and_messages_for_the_date,
    get_discipline_violation_text,
    get_available_masters,
    delete_selected_masters,
    get_working_masters_chats_ids,
    get_working_masters_tg_ids,
    get_available_masters_and_admins,
    get_day_off_masters_ids
)
from services.day_off_services import set_day_off_for_masters
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
    GENERAL_CLEANING,
    GENERAL_CLEANING_SELECT_TEXT,
    GENERAL_CLEANING_DATE_ERROR_TEXT,
    GENERAL_CLEANING_SCHEDULED_MESSAGE,
    GENERAL_CLEANING_ARCHIVE_BTN,
    AVAILABLE_MASTERS,
    MANAGER_ADDED,
    MANAGER_DELETED
)
import logging
from forms.forms import (
    DateSelectState,
    MastersSelectState,
    SelectWorkingMastersForTomorrow
)
from keyboards.keyboards import (
    admin_keyboard,
    master_choose_keyboard,
    general_cleaning_start_kb,
    general_cleanings_archive_kb,
    general_cleaning_accept_kb,
    edit_masters_kb,
    select_working_masters_kb,
    masters_select_request_kb
)
from services.users_services import update_username
from services.general_cleaning_services import (
    get_or_create_general_cleaning,
    get_general_cleanings,
    get_general_cleaning_images_with_category_for_date
)
from forms.forms import GeneralCleaningState
from senders.senders import send_general_cleaning_message
from services.general_cleaning_reaction_services import (
    get_general_cleaning_reactions,
    process_reactions_to_text
)
from services.users_services import (
    set_master_is_manager,
    set_master_is_not_manager
)


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


@admin_handlers_router.message(F.text == AVAILABLE_MASTERS)
async def get_masters(message: Message) -> None:
    logging.info(f"get available masters from {message.chat.id}")

    user = await get_master(message.chat.id)
    user_id = user.id
    username = message.from_user.full_name
    await update_username(user_id, username)
    if not user or not user.is_manager:
        await message.reply(USER_IS_NOT_MANAGER)
        return

    available_masters = await get_available_masters_and_admins()
    message_text = "\n".join([convert_master_data_to_text(master) for master in available_masters])
    reply_markup = edit_masters_kb(available_masters)
    await message.reply(message_text, reply_markup=reply_markup)


@admin_handlers_router.callback_query(F.data.startswith("admin_add"))
async def process_add_admin(callback_query: CallbackQuery) -> None:

    data = callback_query.data.split(":")
    master_id = int(data[1])
    await set_master_is_manager(master_id)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(MANAGER_ADDED)


@admin_handlers_router.callback_query(F.data.startswith("admin_remove"))
async def process_remove_admin(callback_query: CallbackQuery) -> None:
    data = callback_query.data.split(":")
    master_id = int(data[1])
    await set_master_is_not_manager(master_id)
    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(MANAGER_DELETED)


@admin_handlers_router.callback_query(F.data == "select_working_masters")
async def process_select_working_masters_request(callback_query: CallbackQuery, state: FSMContext) -> None:
    logging.info(f"Assign workers for tomorrow")
    #TODO: Убрать весь старый функционал назначения выходного
    await state.set_state(SelectWorkingMastersForTomorrow.select_master)
    available_masters = await get_available_masters()
    selected_masters = dict()
    await state.update_data(available_masters=available_masters, selected_masters=selected_masters)
    await callback_query.answer()
    await callback_query.message.delete()
    message_text = "Выбрать мастера:"
    reply_markup = select_working_masters_kb(available_masters, selected_masters)
    await callback_query.message.answer(message_text, reply_markup=reply_markup)


@admin_handlers_router.callback_query(
    F.data == "cancel_masters_select",
    SelectWorkingMastersForTomorrow.select_master
)
async def cancel_masters_select(callback_query: CallbackQuery, state: FSMContext) -> None:
    logging.info(f"Cancel masters select from {callback_query.message.chat.id}")
    await state.clear()
    await callback_query.answer()
    await callback_query.message.delete()
    message_text = "Выбор сотрудников на завтра был отменен"
    reply_markup = masters_select_request_kb()
    await callback_query.message.answer(message_text, reply_markup=reply_markup)


@admin_handlers_router.callback_query(
    F.data == "submit_masters_select",
    SelectWorkingMastersForTomorrow.select_master
)
async def submit_masters_select(callback_query: CallbackQuery, state: FSMContext) -> None:
    logging.info(f"Submit masters select from {callback_query.message.chat.id}")

    state_data = await state.get_data()
    selected_masters = state_data["selected_masters"]

    selected_masters_names = [val for val in selected_masters.values()]
    selected_masters_ids = [key for key in selected_masters.keys()]

    message_text = "Выбраны на работу завтра:\n" + "\n".join(selected_masters_names)

    tomorrow = (datetime.today() + timedelta(days=1)).date()

    day_off_masters_ids = await get_day_off_masters_ids(selected_masters_ids)

    logging.debug(f"{selected_masters_ids=} {day_off_masters_ids=}")

    await set_day_off_for_masters(day_off_masters_ids, tomorrow)

    await callback_query.answer()
    await callback_query.message.delete()
    await callback_query.message.answer(message_text, reply_markup=admin_keyboard)

    await state.clear()


@admin_handlers_router.callback_query(
    F.data.startswith("assign_master"),
    SelectWorkingMastersForTomorrow.select_master
)
async def process_assign_master_to_working_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    logging.debug("process_assign_master_to_working_query")
    data = callback_query.data.split(":")
    master_id = int(data[1])
    state_data = await state.get_data()
    selected_masters = state_data["selected_masters"]
    available_masters = state_data["available_masters"]
    master_name = available_masters.pop(master_id)
    selected_masters[master_id] = master_name
    reply_markup = select_working_masters_kb(
        available_masters,
        selected_masters,
    )
    selected_masters_names = [val for val in selected_masters.values()]
    logging.debug(f"{selected_masters_names=}")
    message_text = "Выбраны на работу завтра:\n" + "\n".join(selected_masters_names)

    await callback_query.answer()
    await callback_query.message.delete()

    await callback_query.message.answer(message_text, reply_markup=reply_markup)


@admin_handlers_router.callback_query(
    F.data.startswith("remove_master"),
    SelectWorkingMastersForTomorrow.select_master
)
async def process_remove_master_from_working_query(callback_query: CallbackQuery, state: FSMContext) -> None:
    logging.debug("process_remove_master_from_working_query")
    data = callback_query.data.split(":")
    master_id = int(data[1])
    state_data = await state.get_data()
    selected_masters = state_data["selected_masters"]
    available_masters = state_data["available_masters"]
    master_name = selected_masters.pop(master_id)
    available_masters[master_id] = master_name

    logging.debug(f"{selected_masters=} {available_masters=}")

    reply_markup = select_working_masters_kb(
        available_masters,
        selected_masters,
    )
    selected_masters_names = [val for val in selected_masters.values()]
    message_text = "Выбраны на работу завтра:\n" + "\n".join(selected_masters_names)

    await callback_query.answer()
    await callback_query.message.delete()

    await callback_query.message.answer(message_text, reply_markup=reply_markup)


@admin_handlers_router.message(F.text == DELETE_MASTERS)
async def delete_workers(message: Message, state: FSMContext) -> None:
    logging.info(f"Assign workers for deletion")
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
    await state.set_state(GeneralCleaningState.general_cleaning_select_date)
    await message.answer(GENERAL_CLEANING_SELECT_TEXT)


@admin_handlers_router.message(F.text, GeneralCleaningState.general_cleaning_select_date)
async def create_general_cleaning(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        date = parse_date_from_message_text(message.text)
    except ValueError as e:
        logging.error(e)
        await message.reply(DATE_ERROR_TEXT, reply_markup=admin_keyboard)
        return
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if date < today:
        await message.reply(GENERAL_CLEANING_DATE_ERROR_TEXT, reply_markup=admin_keyboard)
        return
    elif date == today:
        await send_general_cleaning_message(message.bot, date)

    general_cleaning = await get_or_create_general_cleaning(date)

    await message.reply(
        GENERAL_CLEANING_SCHEDULED_MESSAGE.format(date=date.replace(hour=16)),
        reply_markup=admin_keyboard
    )
    masters_ids = await get_working_masters_tg_ids()
    for master_id in masters_ids:
        try:
            await message.bot.send_message(
                master_id,
                text = f"Генеральная уборка назначена на {date}",
                reply_markup=general_cleaning_accept_kb(general_cleaning.id)
            )
        except Exception as e:
            logging.warning(e)


@admin_handlers_router.message(F.text == GENERAL_CLEANING_ARCHIVE_BTN)
async def process_general_cleaning_archive(message: Message) -> None:
    start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=365)
    general_cleanings = await get_general_cleanings(start_date)
    await message.answer(
        "Выберите интересующий Вас ПХД:",
        reply_markup=general_cleanings_archive_kb(general_cleanings)
    )


@admin_handlers_router.callback_query(F.data.startswith("archive_gc"))
async def process_selected_general_cleaning(callback_query: CallbackQuery) -> None:
    data = callback_query.data.split(":")
    general_cleaning_id = int(data[1])
    general_cleaning_date = datetime.strptime(data[2], "%d-%m-%Y").date()

    reactions = await get_general_cleaning_reactions(general_cleaning_id)
    message_text = process_reactions_to_text(reactions)

    await callback_query.answer()

    try:
        await callback_query.message.delete()
    except TelegramBadRequest as e:
        logging.warning(f"BAD REQUEST: {e}")

    chunk_size = 4096
    messages_texts = [message_text[i : i + chunk_size] for i in range(0, len(message_text), chunk_size)]
    for message_text in messages_texts:
        await callback_query.message.answer(text=message_text, parse_mode=ParseMode.MARKDOWN_V2)

    images = await get_general_cleaning_images_with_category_for_date(general_cleaning_date)
    for image in images:
        caption =  f"{image.name}: {image.category}"
        await callback_query.message.answer_photo(
            photo=FSInputFile(image.link),
            caption=caption
        )


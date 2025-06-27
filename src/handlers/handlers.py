from datetime import datetime, timedelta

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
    REGISTRATION_REJECT_MESSAGE,
    UPDATE_USERNAME_TEXT,
    DAY_OFF_BTN,
    DAY_OFF_TEXT,
    DAY_OFF_TEXT_TO_ADMIN,
    GENERAL_CLEANING_BTN,
    GENERAL_CLEANING_TEXT,
    GENERAL_CLEANING_FINISH_TEXT,
    GENERAL_CLEANING_CONTINUE_TEXT,
    INVALID_ACTION_TEXT,
    ADD_PHOTO_TEXT,
    PHOTO_ADDED_SUCCESS_TEXT,
    SHIFT_SUPERVISOR_BTN,
    SHIFT_SUPERVISOR_TEXT,
    SHIFT_SUPERVISOR_FINISH_TEXT,
    SHIFT_SUPERVISOR_CONTINUE_TEXT,
    VACATION_BTN,
    VACATION_TEXT,
    VACATION_CANCEL_TEXT,
    VACATION_START_TEXT,
    TOMORROW_DAY_OFF_TEXT,
    CANCEL_DAY_OFF_TEXT,
    DAY_OFF_SCHEDULED_TEXT
)
from services.handlers_services import (
    get_master,
    save_image,
    create_master_and_schedule
    )
from keyboards.keyboards import (
    master_keyboard,
    admin_keyboard,
    general_cleaning_kb,
    get_another_photo_kb,
    shift_supervisor_kb,
    vacation_kb,
    day_off_kb
)
from forms.forms import (
    StartWorkForm,
    EndWorkForm,
    GeneralCleaningState,
    AddPhotoState,
    ShiftSupervisorState,
    VacationSelectState,
    DayOffSelectState
)
import logging
from senders.senders import (
    send_not_registered_message,
    send_registration_request_to_admin
)
from services.users_services import (
    register_user,
    reject_user,
    update_username,
    get_manager_tg_ids_from_db
)
from services.day_off_services import (
    create_day_off,
    create_vacation,
    get_day_offs_for_closest_three_days,
    create_day_off_for_master
)
from services.telegram_services import delete_callback_query_message, delete_message
from static_data.static_data import GENERAL_CLEANING_CHECKLIST, SHIFT_SUPERVISOR_CHECKLIST
from copy import deepcopy


handlers_router = Router()


@handlers_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    logging.info(f"Start command from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user:
        await send_registration_request_to_admin(message)
        await send_not_registered_message(message)
        return

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


@handlers_router.message(Command("name"))
async def handle_update_username(message: Message) -> None:
    logging.info(f"Start command from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user:
        await send_registration_request_to_admin(message)
        await send_not_registered_message(message)
        return
    username = message.from_user.full_name
    user_id = user.id
    await update_username(user_id, username)
    await message.answer(UPDATE_USERNAME_TEXT.format(username=username))


@handlers_router.message(F.text == "Приступил к работе")
async def start_work_handler(message: Message, state: FSMContext) -> None:
    logging.info(f"Start work button from {message.chat.id}")
    user = await get_master(message.chat.id)
    if not user:
        await send_registration_request_to_admin(message)
        return await send_not_registered_message(message)
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
    user = await get_master(message.chat.id)
    if not user:
        await send_registration_request_to_admin(message)
        return await send_not_registered_message(message)
    await state.set_state(EndWorkForm.end_work)
    await message.answer(MASTER_END_WORK_TEXT, reply_markup=master_keyboard)


@handlers_router.message(EndWorkForm.end_work, F.photo)
async def process_start_work_image(message: Message, state: FSMContext) -> None:
    logging.info(f"End work image from {message.chat.id}")
    await save_image(message)
    await state.clear()
    await message.answer(MASTER_END_WORK_IMAGE_RECEIVED_TEXT, reply_markup=master_keyboard)

    master = await get_master(message.chat.id)
    master_id = master.id
    closest_day_offs = await get_day_offs_for_closest_three_days(master_id)
    if closest_day_offs:
        return
    response = await message.answer(
        TOMORROW_DAY_OFF_TEXT,
        reply_markup=day_off_kb(),
    )
    await state.set_state(DayOffSelectState.day_off_select)
    await state.update_data(message_id=response.message_id)


@handlers_router.callback_query(F.data == "start_day_off", DayOffSelectState.day_off_select)
async def start_day_off_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    message_id = data["message_id"]
    await delete_callback_query_message(callback_query, message_id)

    await state.clear()
    await callback_query.answer()
    await callback_query.message.answer(
        DAY_OFF_SCHEDULED_TEXT
    )

    master = await get_master(callback_query.message.chat.id)
    master_id = master.id

    for day in range(1, 3):
        day_off_date = datetime.today().date() + timedelta(days=day)
        day_off = await create_day_off_for_master(master_id, day_off_date)
        logging.info(f"Day off created: {day_off}")


@handlers_router.callback_query(F.data == "cancel_day_off", DayOffSelectState.day_off_select)
async def cancel_day_off_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    message_id = data["message_id"]
    await delete_callback_query_message(callback_query, message_id)

    await state.clear()
    await callback_query.answer()
    await callback_query.message.answer(
        CANCEL_DAY_OFF_TEXT
    )


@handlers_router.callback_query(F.data == 'start_gc')
async def process_general_cleaning_btn(callback_query: CallbackQuery, state: FSMContext) -> None:
    user = await get_master(callback_query.message.chat.id)
    if not user:
        await send_registration_request_to_admin(callback_query.message)
        await send_not_registered_message(callback_query.message)
        return
    await state.set_state(GeneralCleaningState.general_cleaning)
    elements = deepcopy(GENERAL_CLEANING_CHECKLIST)

    reply_markup = general_cleaning_kb(elements)
    response = await callback_query.message.answer(GENERAL_CLEANING_TEXT, reply_markup=reply_markup)
    message_id = response.message_id
    await state.update_data(elements=elements, message_id=message_id)
    await callback_query.answer()


@handlers_router.callback_query(F.data.startswith("gc:"), GeneralCleaningState.general_cleaning)
async def change_cleaning_photo_expectation_message(
        callback_query: CallbackQuery,
        state: FSMContext
) -> None:
    action = callback_query.data.split(":")[1]
    data = await state.get_data()

    message_id = data.get("message_id")
    await delete_callback_query_message(callback_query, message_id)

    elements = data.get("elements")
    current_element = list(filter(lambda x: x.get("name") == action, elements))[0]

    text = current_element.get("text")
    response = await callback_query.message.answer(text=text)
    logging.info(response)
    message_id = response.message_id
    await state.update_data(action=action, message_id=message_id)


@handlers_router.message(F.text == DAY_OFF_BTN)
async def process_day_off_handler(message: Message) -> None:
    chat_id = message.chat.id
    logging.info(f"Day off message from {chat_id}")
    user = await get_master(message.chat.id)
    if not user:
        await send_registration_request_to_admin(message)
        await send_not_registered_message(message)
        return
    await message.answer(DAY_OFF_TEXT, reply_markup=master_keyboard)
    await create_day_off(chat_id)
    username = message.from_user.full_name
    message_text = DAY_OFF_TEXT_TO_ADMIN.format(username=username)
    managers_chat_ids = await get_manager_tg_ids_from_db()
    for manager_id in managers_chat_ids:
        await message.bot.send_message(manager_id, message_text, reply_markup=admin_keyboard)


@handlers_router.message(F.photo, GeneralCleaningState.general_cleaning)
async def process_cleaning_photo(message: Message, state: FSMContext):

    await save_image(message)

    data = await state.get_data()
    message_id = data.get("message_id")
    await delete_message(message, message_id)

    elements = data.get("elements")
    action = data.get("action")

    try:
        current_element = list(filter(lambda x: x.get("name") == action, elements))[0]
    except IndexError as e:
        logging.debug(e)
        text = INVALID_ACTION_TEXT
        await message.answer(text=text, reply_markup=general_cleaning_kb(elements))
        return

    elements.remove(current_element)

    if not elements:
        text = GENERAL_CLEANING_FINISH_TEXT
        reply_markup = get_another_photo_kb
        await message.answer(text=text, reply_markup=reply_markup)
        await state.clear()
        return
    reply_markup = general_cleaning_kb(elements)
    response = await message.answer(GENERAL_CLEANING_CONTINUE_TEXT, reply_markup=reply_markup)
    message_id = response.message_id
    await state.update_data(elements=elements, message_id=message_id)


@handlers_router.message(GeneralCleaningState.general_cleaning)
async def process_invalid_message(message: Message, state: FSMContext):
    data = await state.get_data()

    message_id = data.get("message_id")
    await delete_message(message, message_id)

    elements = data.get("elements")
    text = INVALID_ACTION_TEXT

    reply_markup = general_cleaning_kb(elements)
    response = await message.answer(
            text=text,
            reply_markup=reply_markup
        )
    await state.update_data(message_id=response.message_id)


@handlers_router.callback_query(F.data == "add_photo")
async def process_add_photo_button(callback_query, state: FSMContext) -> None:
    message_id = callback_query.message.message_id
    await delete_callback_query_message(callback_query, message_id)
    await state.set_state(AddPhotoState.add_photo)
    response = await callback_query.message.answer(ADD_PHOTO_TEXT)
    await state.update_data(message_id=response.message_id)


@handlers_router.message(F.photo, AddPhotoState.add_photo)
async def process_additional_photo(message: Message, state: FSMContext) -> None:
    await save_image(message)
    data = await state.get_data()
    message_id = data.get("message_id")
    await delete_message(message, message_id)
    await message.answer(PHOTO_ADDED_SUCCESS_TEXT, reply_markup=get_another_photo_kb)


@handlers_router.message(AddPhotoState.add_photo)
async def process_invalid_message(message: Message, state: FSMContext):
    data = await state.get_data()

    message_id = data.get("message_id")
    await delete_message(message, message_id)

    text = INVALID_ACTION_TEXT

    response = await message.answer(
            text=text,
        )
    await state.update_data(message_id=response.message_id)


@handlers_router.message(F.text == SHIFT_SUPERVISOR_BTN)
async def process_general_cleaning_btn(message: Message, state: FSMContext) -> None:
    user = await get_master(message.chat.id)
    if not user:
        await send_registration_request_to_admin(message)
        await send_not_registered_message(message)
        return
    await state.set_state(ShiftSupervisorState.shift_supervisor)
    elements = deepcopy(SHIFT_SUPERVISOR_CHECKLIST)

    reply_markup = shift_supervisor_kb(elements)
    response = await message.answer(SHIFT_SUPERVISOR_TEXT, reply_markup=reply_markup)
    message_id = response.message_id
    await state.update_data(elements=elements, message_id=message_id)


@handlers_router.callback_query(F.data.startswith("shs:"), ShiftSupervisorState.shift_supervisor)
async def change_shift_photo_expectation_message(
        callback_query: CallbackQuery,
        state: FSMContext
) -> None:
    action = callback_query.data.split(":")[1]
    data = await state.get_data()

    message_id = data.get("message_id")
    await delete_callback_query_message(callback_query, message_id)

    elements = data.get("elements")
    current_element = list(filter(lambda x: x.get("name") == action, elements))[0]

    text = current_element.get("text")
    response = await callback_query.message.answer(text=text)
    logging.info(response)
    message_id = response.message_id
    await state.update_data(action=action, message_id=message_id)


@handlers_router.message(F.photo, ShiftSupervisorState.shift_supervisor)
async def process_shift_photo(message: Message, state: FSMContext):

    await save_image(message)

    data = await state.get_data()
    message_id = data.get("message_id")
    await delete_message(message, message_id)

    elements = data.get("elements")
    action = data.get("action")

    try:
        current_element = list(filter(lambda x: x.get("name") == action, elements))[0]
    except IndexError as e:
        logging.debug(e)
        text = INVALID_ACTION_TEXT
        response = await message.answer(text=text, reply_markup=shift_supervisor_kb(elements))
        return

    elements.remove(current_element)

    if not elements:
        text = SHIFT_SUPERVISOR_FINISH_TEXT
        reply_markup = get_another_photo_kb
        await message.answer(text=text, reply_markup=reply_markup)
        await state.clear()
        return
    reply_markup = shift_supervisor_kb(elements)
    response = await message.answer(SHIFT_SUPERVISOR_CONTINUE_TEXT, reply_markup=reply_markup)
    message_id = response.message_id
    await state.update_data(elements=elements, message_id=message_id)


@handlers_router.message(ShiftSupervisorState.shift_supervisor)
async def process_shift_invalid_message(message: Message, state: FSMContext):
    data = await state.get_data()

    elements = data.get("elements")
    text = INVALID_ACTION_TEXT

    reply_markup = shift_supervisor_kb(elements)
    response = await message.answer(
            text=text,
            reply_markup=reply_markup
        )
    await state.update_data(message_id=response.message_id)


@handlers_router.message(F.text == VACATION_BTN)
async def process_vacation_btn(message: Message, state: FSMContext) -> None:
    await state.set_state(VacationSelectState.vacation_select)
    response = await message.answer(
        VACATION_TEXT,
        reply_markup=vacation_kb()
    )
    message_id = response.message_id
    await state.update_data(message_id=message_id)


@handlers_router.callback_query(F.data == "cancel_vacation", VacationSelectState.vacation_select)
async def cancel_vacation(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    message_id = data.get("message_id")
    await delete_callback_query_message(callback_query, message_id)
    await state.clear()
    await callback_query.message.answer(VACATION_CANCEL_TEXT)
    await callback_query.answer()


@handlers_router.callback_query(F.data == "start_vacation", VacationSelectState.vacation_select)
async def start_vacation(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    message_id = data.get("message_id")
    await delete_callback_query_message(callback_query, message_id)
    await state.clear()

    master = await get_master(callback_query.message.chat.id)
    master_id = master.id
    await create_vacation(master_id)

    await callback_query.message.answer(VACATION_START_TEXT)
    await callback_query.answer()
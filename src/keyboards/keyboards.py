from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, User, InlineKeyboardButton
from static_text.static_text import (
    REGISTRATION_CONFIRM_BTN,
    registration_confirm_callback_data,
    REGISTRATION_REJECT_BTN,
    registration_reject_callback_data,
    START_WORK_BTN,
    END_WORK_BTN,
    SCHEDULE_BTN,
    WORKPLACE_IMAGE_BTN,
    SELECTED_DATE_IMAGE_BTN,
    DISCIPLINE_VIOLATION_BTN,
    GENERAL_CLEANING_BTN,
    SHIFT_SUPERVISOR_BTN,
    DELETE_MASTERS,
    AVAILABLE_MASTERS,
    GENERAL_CLEANING_ARCHIVE_BTN
)
from static_data.static_data import GeneralCleaningDict, ShiftSupervisorDict
from services.general_cleaning_services import GeneralCleaningDict


master_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=START_WORK_BTN),
                                    ],
                [
                    KeyboardButton(text=END_WORK_BTN),
                ],
                [
                    KeyboardButton(text=SHIFT_SUPERVISOR_BTN)
                ],
            ],
            resize_keyboard=True,
        )

admin_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                KeyboardButton(text=SCHEDULE_BTN),
                KeyboardButton(text=WORKPLACE_IMAGE_BTN)
                ],
                [
                KeyboardButton(text=SELECTED_DATE_IMAGE_BTN),
                KeyboardButton(text=DISCIPLINE_VIOLATION_BTN)
                ],
                [KeyboardButton(text=AVAILABLE_MASTERS)],
                [KeyboardButton(text=DELETE_MASTERS)],
                [KeyboardButton(text=GENERAL_CLEANING_BTN)],
                [KeyboardButton(text=GENERAL_CLEANING_ARCHIVE_BTN)],
            ],
            resize_keyboard=True,
        )


def confirm_registration_kb(user: User) -> InlineKeyboardMarkup:
    """Returns the inline keyboard for confirming a registration request."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=REGISTRATION_CONFIRM_BTN,
                    callback_data=f"{registration_confirm_callback_data}:{user.id}:{user.username}",
                ),
                InlineKeyboardButton(
                    text=REGISTRATION_REJECT_BTN,
                    callback_data=f"{registration_reject_callback_data}:{user.id}:{user.username}",
                ),
            ]
        ]
    )
    return keyboard


def general_cleaning_kb(elements: list[GeneralCleaningDict]):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=element.get('readable_name'),
                    callback_data=f"gc:{element.get('name')}"
                )
            ]
            for element in elements
        ]
    )
    return keyboard


get_another_photo_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить фото", callback_data="add_photo")]
            ]
    )


def shift_supervisor_kb(elements: list[ShiftSupervisorDict]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=element.get('readable_name'),
                    callback_data=f"shs:{element.get('name')}"
                )
            ]
            for element in elements
        ]
    )
    return keyboard


def master_choose_keyboard(masters: dict[int, str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=master_name,
                    callback_data=f"mchs:{master_id}"
                )
            ]
            for master_id, master_name in masters.items()
        ] +
        [
            [
                InlineKeyboardButton(
                    text="Завершить выбор",
                    callback_data="finish_mchs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Сбросить выбор",
                    callback_data="cancel_mchs"
                )
            ]
        ]
    )
    return keyboard


def general_cleaning_start_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(
                text="Загрузить фото",
                callback_data="start_gc"
            )
                ]
        ]
    )
    return keyboard


def general_cleaning_accept_kb(general_cleaning_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Буду!",
                    callback_data=f"accept_gc:{general_cleaning_id}:1"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Не буду!",
                    callback_data=f"accept_gc:{general_cleaning_id}:0"
                )
            ]
        ]
    )
    return keyboard


def general_cleanings_archive_kb(general_cleanings: list[GeneralCleaningDict]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=general_cleaning.get("date").strftime("%d-%m-%Y"),
                    callback_data=f"archive_gc:{general_cleaning.get('id')}:{general_cleaning.get('date').strftime('%d-%m-%Y')}"
                )
            ]
            for general_cleaning in general_cleanings
        ]
    )
    return keyboard


def edit_masters_kb(masters: list[dict[str, int| str| bool]]) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for master in masters:
        if master["is_manager"]:
            inline_keyboard.append(
                [
                        InlineKeyboardButton(
                        text=f"Удалить из менеджеров: {master['name']}",
                        callback_data=f"admin_remove:{master['id']}"
                    )
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"Добавить менеджера: {master['name']}",
                        callback_data=f"admin_add:{master['id']}"
                    )
                ]
            )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )
    return keyboard


def masters_select_request_kb():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Выбрать мастеров",
                    callback_data="select_working_masters"
                )
            ]
        ]
    )
    return keyboard


def select_working_masters_kb(
    available_masters: dict[int, str],
    selected_masters: dict[int, str]
):
    cancel_btn = [
        InlineKeyboardButton(
            text="ОТМЕНА ",
            callback_data="cancel_masters_select"
        )
    ]
    submit_btn = [
        InlineKeyboardButton(
            text="ПОДТВЕРДИТЬ",
            callback_data="submit_masters_select"
        )
    ]
    available_masters_btns = [
        [
            InlineKeyboardButton(
                text=f"Добавить: {value}",
                callback_data=f"assign_master:{key}"
            )
        ]
    for key, value in available_masters.items()]
    selected_masters_btns = [
        [
            InlineKeyboardButton(
                text=f"Убрать: {value}",
                callback_data=f"remove_master:{key}"
        )]
    for key, value in selected_masters.items()]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=available_masters_btns + selected_masters_btns + [cancel_btn] + [submit_btn]

    )
    return keyboard

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, User, InlineKeyboardButton
from static_text.static_text import (
    REGISTRATION_CONFIRM_BTN,
    registration_confirm_callback_data,
    REGISTRATION_REJECT_BTN,
    registration_reject_callback_data,
    START_WORK_BTN,
    END_WORK_BTN,
    DAY_OFF_BTN,
    SCHEDULE_BTN,
    WORKPLACE_IMAGE_BTN,
    SELECTED_DATE_IMAGE_BTN,
    DISCIPLINE_VIOLATION_BTN,
    GENERAL_CLEANING_BTN,
    SHIFT_SUPERVISOR_BTN,
    DELETE_MASTERS,
    DAY_OFF_BTN,
    VACATION_BTN
)
from static_data.static_data import GeneralCleaningDict, ShiftSupervisorDict


master_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=START_WORK_BTN),
                                    ],
                [
                    KeyboardButton(text=END_WORK_BTN),
                ],
                [
                    KeyboardButton(text=DAY_OFF_BTN),
                ],
                [
                    KeyboardButton(text=SHIFT_SUPERVISOR_BTN)
                ],
                [
                    KeyboardButton(text=VACATION_BTN)
                ]
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
                [KeyboardButton(text=DELETE_MASTERS)],
                [KeyboardButton(text=GENERAL_CLEANING_BTN)],
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


def vacation_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отпуск на 7 дней!",
                    callback_data="start_vacation:7"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Отпуск на 14 дней!",
                    callback_data="start_vacation:14"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Отмена",
                    callback_data="cancel_vacation"
                )
            ]
        ]
    )
    return keyboard


def day_off_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Выходной!",
                    callback_data="start_day_off"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Нет",
                    callback_data="cancel_day_off"
                )
            ]
        ]
    )
    return keyboard
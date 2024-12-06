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
    SHIFT_SUPERVISOR_BTN
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
                    KeyboardButton(text=DAY_OFF_BTN)
                ],
                [
                    KeyboardButton(text=GENERAL_CLEANING_BTN)
                ],
                [
                    KeyboardButton(text=SHIFT_SUPERVISOR_BTN)
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
                ]
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


def shift_supervisor_kb(elements: list[ShiftSupervisorDict]):
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
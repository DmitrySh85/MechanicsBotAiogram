from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


master_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Приступил к работе"),
                    KeyboardButton(text="Закончил работу"),
                ]
            ],
            resize_keyboard=True,
        )

admin_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                KeyboardButton(text="Расписание на сегодня"),
                KeyboardButton(text="Фото рабочего места"),
                ]
            ],
            resize_keyboard=True,
        )
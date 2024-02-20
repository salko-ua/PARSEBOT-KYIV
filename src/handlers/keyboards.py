from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def edit_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = ["Додати номер ✏️", "Репост в канал ▶️"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup(resize_keyboard=True)


def repost_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = ["Репост в канал ▶️"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup(resize_keyboard=True)

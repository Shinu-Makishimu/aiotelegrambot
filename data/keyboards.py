from aiogram import types
# from settings import cb
from aiogram.utils.callback_data import CallbackData


cb = CallbackData("post", "action")


def main_keyboard() -> types.InlineKeyboardMarkup:
    """
    Генерация клавиатуры
    :return:
    """
    buttons = [
        types.InlineKeyboardButton(text='Low price', callback_data=cb.new(action='low')),
        types.InlineKeyboardButton(text='Best deal', callback_data=cb.new(action='best')),
        types.InlineKeyboardButton(text='High price', callback_data=cb.new(action='high')),
        types.InlineKeyboardButton(text='My history', callback_data=cb.new(action='history')),
        types.InlineKeyboardButton(text='Settings', callback_data=cb.new(action='settings')),
        types.InlineKeyboardButton(text='Help', callback_data=cb.new(action='help'))
    ]
    keyboard = types.InlineKeyboardMarkup().add(*buttons)
    return keyboard

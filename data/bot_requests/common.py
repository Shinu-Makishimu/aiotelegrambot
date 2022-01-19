from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    text = 'This bot can find hotels in any city in the world!\n' \
           'Send me command or tap /help for help\n'
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Action cancelled', reply_markup=types.ReplyKeyboardRemove())


async def cmd_help(message: types.Message):
    text = 'About this bot\n' \
           'Bot using API hotels.com \n' \
           'Информация из выдачи может не соответствовать действительности\n' \
           'Бот имеет ограниченный функционал и построен только для опробования библиотеки aiogram\n' \
           'Checkin: today, checkout tomorrow. Price for one night!' \
           'Short instructions:\n' \
           'Commands lowprice, highprice: searching cheap and expensive hotels .\n' \
           'Question order: city, hotels numbers, photo numbers, currency, save history or not\n' \
           'Command bestdeal: same questions, plus radius from centre and min, max price\n' \
           'Следуйте командам бота и не пытайтесь его шатать!'
    await message.answer(text)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start', state="*")
    dp.register_message_handler(cmd_cancel, commands='cancel', state="*")
    dp.register_message_handler(cmd_help, commands='help')
    dp.register_message_handler(cmd_cancel, Text(equals="cancel", ignore_case=True), state="*")

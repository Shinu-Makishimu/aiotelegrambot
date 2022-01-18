from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    text = 'Это бот для поиска отелей в любом городе мира!\n' \
           'Выбери команду из списка команд.\n' \
           'Или отправь боту /help'
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())


async def cmd_help(message: types.Message):
    text = 'Раздел помощи по боту.\n' \
           'Бот работает на основе API hotels.com \n' \
           'Информация из выдачи может не соответствовать действительности\n' \
           'Бот имеет ограниченный функционал и построен только для опробования библиотеки aiogram\n' \
           'Дата заезда - сегодня, выезда - завтра. цена за одну ночь!' \
           'Краткая инструкция:\n' \
           'команды lowprice, highprice: поиск дешевых и дорогих отелей соотвуетсвенно.\n' \
           'Порядок опроса: город, количество отелей, количество фото, валюта, сохранять историю или нет\n' \
           'Команда bestdeal: всё тоже самое, добавляется радиус от центра и диапазон цены\n' \
           'Следуйте командам бота и не пытайтесь его шатать!'
    await message.answer(text)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start', state="*")
    dp.register_message_handler(cmd_cancel, commands='cancel', state="*")
    dp.register_message_handler(cmd_help, commands='help')
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")

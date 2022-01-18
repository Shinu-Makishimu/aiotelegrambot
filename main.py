# from aiogram import  Bot, Dispatcher, types
# from loguru import logger
# from aiogram.utils import executor
#
# from aiogram.utils.callback_data import CallbackData
# from aiogram.types import BotCommand
# #начинаем пробовать конечные автоматы
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher.filters.state import State, StatesGroup
#
# #  дальнейшем мемори стораж заменить на редис
# from data import keyboards
# import settings
# from data.requests.lowprice import register_handlers_lowprice
#
#
#
# logger.configure(**settings.logger_config)
# logger.info("\n" + "\\" * 50 + 'new session started' + "//" * 50 + "\n")
#
# bot = Bot(token=settings.API_TOKEN)
#
# #диспетчера
# dp = Dispatcher(bot)
# #фабрика коллбеков
# cb = CallbackData("post", "action")
#
# #задаём команды
# async def set_commands(bot: Bot):
#     commands = [
#         BotCommand(command="/lowprice", description="низкая цена отелей"),
#         BotCommand(command="/main", description="глагне"),
#         BotCommand(command="/cancel", description="Отменить текущее действие")
#     ]
#     await bot.set_my_commands(commands)
#
#
# @dp.message_handler(commands="start")
# async def cmd_start(message: types.Message):
#     """
#     Реакция на кнопку старт. показываем заглавную клавиатуру
#     """
#     logger.info(f'Function{cmd_start.__name__} was called')
#     message_text = f'Привет пользователь {message.from_user.id}! я бот ты говно!'
#     await message.answer(message_text, reply_markup=keyboards.main_keyboard())
#
#
# @dp.callback_query_handler(cb.filter(action=['low', 'best', 'high']))
# async def main_menu(query: types.CallbackQuery, callback_data: dict):
#     """
#     Обрабатываем нажатие кнопок меню
#     :param query:
#     :param callback_data:
#     :return:
#     """
#     logger.info(f'Function{main_menu.__name__} was called with {callback_data}')
#     await query.answer()
#     callback_data_action = callback_data['action']
#     await bot.edit_message_text(
#         f'ты нажал кнопку {callback_data_action}, вводи название города',
#         query.from_user.id,
#         query.message.message_id
#     )
#     register_handlers_lowprice(dp)
#
# # и тут вступают в дело конечные автоматы. идет опрос пользователя. город,
#
# try:
#     executor.start_polling(dp, skip_updates=True)
# except Exception as e:
#     logger.warning(f'bot was say crya')
#
###########################################################################################
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from data.bot_requests.lowprice import register_handlers_lowprice
from data.bot_requests.common import register_handlers_common
import settings

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/lowprice", description="показать меню"),
        BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():
    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=settings.API_TOKEN)
    storage = RedisStorage2('localhost', 6379, db=5, pool_size=10, prefix='my_fsm_key')
    dp = Dispatcher(bot, storage=storage)

    # Регистрация хэндлеров
    register_handlers_common(dp)
    register_handlers_lowprice(dp)


    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())

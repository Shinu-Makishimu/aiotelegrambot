import asyncio

from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.redis import RedisStorage2

import settings
from data.bot_requests.common import register_handlers_common
from data.bot_requests.lowprice import register_handlers_lowprice
from data.bot_requests.highprice import register_handlers_highprice
from data.bot_requests.bestdeal import register_handlers_bestdeal





async def set_commands(bot: Bot) -> None:
    """
    This func creates a command menu
    :param bot: bot object
    :return: None
    """
    commands = [
        BotCommand(command="/bestdeal", description="Best deal"),
        BotCommand(command="/highprice", description="Expensive hotels"),
        BotCommand(command="/lowprice", description="Cheap hotels"),
        BotCommand(command="/cancel", description="Undo current action")
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    """
    In this function, a bot object is created, storage and dispatcher are initialized, handlers are registered.
    :return:
    """
    logger.configure(**settings.logger_config)
    logger.info('\n' + '\\' * 50 + 'new session start' + '//' * 50 + '\n')

    bot = Bot(token=settings.API_TOKEN)
    storage = RedisStorage2('localhost', 6379, db=5, pool_size=10, prefix='my_fsm_key')
    dp = Dispatcher(bot, storage=storage)

    register_handlers_common(dp)
    register_handlers_lowprice(dp)
    register_handlers_highprice(dp)
    register_handlers_bestdeal(dp)

    await set_commands(bot)

    await dp.skip_updates()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())

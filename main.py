import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

import config
from yd.yd_api import get_by_stud_id, FILE_PATH_PIE, FILE_PATH_IVT, FILE_PATH_IT

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

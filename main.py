import asyncio
import logging
from aiogram import Bot, Dispatcher
import config
from routers.commands.base_commands import router as cmd_router
from routers.scripts.base_scripts import router as script_router

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(cmd_router)
dp.include_router(script_router)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

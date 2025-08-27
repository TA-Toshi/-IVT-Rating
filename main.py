import asyncio
import logging
from aiogram import Bot, Dispatcher
import config
from routers.commands.base_commands import router as cmd_router
from routers.scripts.base_scripts import router as script_router
from yd.db import get_all_users
from yd.yd_api import check_upd

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
dp.include_router(cmd_router)
dp.include_router(script_router)


async def send_notifications(upds):
    users = await get_all_users()
    upd_students = set()
    for upd in upds:
        upd_students.add(upd[2])

    for chat_id, id_student in users:
        if id_student in upd_students:
            message = "🔔 Внимание! Новые оценки! 🔔\n\n"
            for upd in upds:
                if id_student == upd[2]:
                    message += f"{upd[0][1]} - {upd[1]}\n"

            try:
                await bot.send_message(chat_id, message)
            except Exception as e:
                print(f"Ошибка отправки сообщения {chat_id}: {e}")


async def periodic_check():
    while True:
        # 86400 - сутки
        await asyncio.sleep(86400)
        changes = check_upd([config.FILE_PATH_IVT, config.FILE_PATH_IT, config.FILE_PATH_PIE])
        if changes:
            await send_notifications(changes)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await asyncio.gather(
        dp.start_polling(bot),
        periodic_check()
    )


if __name__ == "__main__":
    asyncio.run(main())

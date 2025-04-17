import asyncio

import aiosqlite


async def add_to_db(telegram_id, student_id):
    async with aiosqlite.connect("yd/tg.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, student_id TEXT)")
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ? AND student_id = ?",
                                  (telegram_id, student_id))
        data = await cursor.fetchone()
        if data is not None:
            return

        await db.execute("INSERT INTO users (telegram_id, student_id) VALUES(?, ?)", (telegram_id, student_id))
        await db.commit()


async def del_from_db(telegram_id, student_id):
    async with aiosqlite.connect("yd/tg.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, student_id TEXT)")
        await db.execute("DELETE FROM users WHERE telegram_id = ? AND student_id = ?", (telegram_id, student_id))
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect("yd/tg.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, student_id TEXT)")
        cursor = await db.execute("SELECT * FROM users")
        return await cursor.fetchall()


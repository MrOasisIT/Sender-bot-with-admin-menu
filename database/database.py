import asyncpg
import asyncio
from asyncpg import Pool


async def create_pool(url:str):
    return await asyncpg.create_pool(dsn = url)

async def create_table(pool:Pool):
    async with pool.acquire() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS users(
                                  user_id BIGINT PRIMARY KEY,
                                  username TEXT,
                                  reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""")

async def create_table2(pool:Pool):
    async with pool.acquire() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS bannedusers(
                                  user_id BIGINT PRIMARY KEY);""")

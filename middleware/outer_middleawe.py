from aiogram import BaseMiddleware
from asyncpg import Pool
from aiogram.types import TelegramObject
from typing import Awaitable,Callable,Dict,Any
import logging

log = logging.getLogger(__name__)

class Outermiddleware(BaseMiddleware):
    def __init__(self,pool):
        self.pool = pool
    
    async def __call__(
            self,
            handler:Callable[[TelegramObject,Dict[str,Any]],Awaitable[Any]],
            event:TelegramObject,
            data:Dict[str,Any]
    ):
        user = data["event_from_user"]
        user_id = user.id
        async with self.pool.acquire() as conn:
            rows = await conn.fetchrow("""SELECT user_id FROM bannedusers WHERE user_id=$1;""",user_id)
            if rows:
                banned_user = rows["user_id"]
                if user_id == banned_user:
                    return
            try:
                return await handler(event,data)
            except Exception as e:
                log.exception("Произошла ошибка в работе бота!")
                
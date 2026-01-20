from aiogram import BaseMiddleware
from typing import Awaitable,Callable,Dict,Any
from aiogram.types import TelegramObject
import asyncpg
from database.database import create_pool
import logging

log = logging.getLogger(__name__)

class DBmiddleware(BaseMiddleware):
    def __init__(self,pool:asyncpg.Pool):
        self.pool = pool

    async def __call__(
            self,
            handler:Callable[[TelegramObject,Dict[str,Any]],Awaitable[Any]],
            event:TelegramObject,
            data:Dict[str,Any]
    ):
        try:
            async with self.pool.acquire() as connection:
                data["db"] = connection
                return await handler(event,data)
        except Exception as e:
            log.exception("Произошла ошибка в работе базы данных")
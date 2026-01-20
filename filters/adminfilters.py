from aiogram.filters import BaseFilter
from aiogram.types import Message

class AdminF(BaseFilter):
    async def __call__(self, message:Message):
        if message.from_user.username == "Pivoed0":
            return True
        else:
            return False
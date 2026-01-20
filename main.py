from aiogram import Bot,Dispatcher
import asyncio
from handlers.admin_menu_handlers import router as router1
from middleware.middleware import DBmiddleware
from database.database import create_pool
from middleware.outer_middleawe import Outermiddleware
import logging
import dotenv
import os

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
DB_URL = os.getenv("DB_URL")

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

log = logging.getLogger(__name__)

if TOKEN:
    log.warning("Токен найден")
    bot = Bot(token = TOKEN)

dp = Dispatcher()

async def main():
    if DB_URL:
        pool = await create_pool(DB_URL)
        if not pool:
            log.warning("Не удалось подключится к базе данных")
            return
    try:
        dp.update.outer_middleware(Outermiddleware(pool))
        dp.update.middleware(DBmiddleware(pool))
        dp.include_routers(router1)
        await bot.delete_webhook(drop_pending_updates=True)
        log.info("Бот запущен")
        await dp.start_polling(bot)
    except Exception as e:
        await pool.close()
        await bot.session.close()
        log.exception("Бот приостановлен возникли ошибки")
    finally:
        await pool.close()
        await bot.session.close()
        log.info("Бот завершил работу")

if __name__ =="__main__":
    try:
        asyncio.run(main())
    except Exception:
        log.exception("Произошла ошибка в запуске main")
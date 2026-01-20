from aiogram import F, Router,Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State,StatesGroup
from filters.adminfilters import AdminF
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError,TelegramRetryAfter
from keyboard.admin_menu import keyboard
import asyncio
import asyncpg
import logging

log = logging.getLogger(__name__)

class Send(StatesGroup):
    text = State()

class Ban(StatesGroup):
    username = State()

class Razban(StatesGroup):
    username = State()

router = Router()

class Reg(StatesGroup):
    data = State()

@router.message(F.from_user.username != "Pivoed0")
async def reg1(message:Message,state:FSMContext,db):
    username = message.from_user.username
    user_id = message.from_user.id
    rows = await db.fetchrow("""SELECT user_id,username FROM users
                             WHERE user_id=$1;""",user_id)
    if not rows:
        await db.execute("""INSERT INTO users(user_id,username) VALUES ($1,$2);""",user_id,username)
        await message.answer("Вы успешно зарегистрированы")
        log.warning("Добавлен новый пользователь %s",user_id)
        return
    db_user_id = rows["user_id"]
    db_username = rows["username"]
    if username != db_username and username is not None:
        await db.execute("""UPDATE users
                            SET username=$1
                            WHERE user_id=$2""",username,user_id)
        await message.answer("Вы уже зарегистрированы")
        log.info("Пользователь %s сменил юзермейм",user_id)
        return
    await message.answer("Вы уже зарегистрированы")
@router.message(Command("start"),AdminF())
async def main_handler(message:Message):
    await message.answer("Вы администратор, выберите функцию",reply_markup = keyboard)

@router.message(F.text == "Отправка",AdminF())
async def handler11(message:Message,state:FSMContext):
    await message.answer("Пожалйста введите текст, который вы отправите пользователям")
    await state.set_state(Send.text)
    
@router.message(Send.text,Command("stop"))
async def stop_fsm1(message:Message,state:FSMContext):
    await state.clear()


@router.message(Send.text)
async def handler12(message:Message,state:FSMContext,bot:Bot,db):
    data = message.text
    rows = await db.fetch("""SELECT user_id FROM users""")
    if not rows:
        await message.answer("У вас нет пользоватлей")
        await state.clear()
        log.info("У бота нету пользоватлей отправка не удалась")
        return
    user_ids = [row["user_id"] for row in rows]
    log.info("Администратор запустил оптравку")
    for user_id in user_ids:
        try:
            await bot.send_message(user_id,data)
            await asyncio.sleep(0.05)
        except TelegramForbiddenError:
            log.info("Пользователь %s заблокировал пользователя",user_id)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await bot.send_message(user_id,data)
            log.info("Телеграмм приостановил отправку")
        except Exception as e:
            log.exception("Произошли технические ошибки")
    await message.answer("Ваше сообщение было отправлено")
    log.info("Отправка завершилась")
    await state.clear()

@router.message(F.text == "Забанить",AdminF())
async def handler21(message:Message,state:FSMContext):
    await message.answer("Введиите имя пользователя которого хотите заблокировать")
    await state.set_state(Ban.username)

@router.message(Ban.username)
async def handler22(message:Message,state:FSMContext,db):
    username = message.text
    data = await db.fetchrow("""SELECT user_id FROM users WHERE username=$1;""",username)
    if not data:
        await message.answer("Пользоватеь не найден")
        await state.clear()
        log.info("Администратор не смог заблокировать пользователя которого не нашел")
        return
    banned_id = data["user_id"]
    already_banned = await db.fetchrow("""SELECT user_id FROM bannedusers WHERE user_id=$1""",banned_id)
    if not already_banned:
        await db.execute("""INSERT INTO bannedusers(user_id) VALUES($1);""",banned_id)
        await message.answer("Пользователь заблокирован")
        log.warning("Администратор заблокировал пользователя %s",banned_id)
        await state.clear()
        return
    await message.answer("Пользователь уже заблокирован")
    log.info("Администратор не смог заблокировать пользователя который был заблокирован %s",banned_id)
    await state.clear()

@router.message(Ban.username,Command("stop"))
async def stop_fsm2(message:Message,state:FSMContext):
    await state.clear()

@router.message(F.text == "Разбанить",AdminF())
async def handler31(message:Message,state:FSMContext):
    await message.answer("Пожалуйста введите имя пользователя которго хотите разблокировать")
    await state.set_state(Razban.username)

@router.message(Razban.username)
async def handler32(message:Message,state:FSMContext,db):
    username = message.text
    data = await db.fetchrow("""SELECT user_id FROM users WHERE username=$1""",username)
    if not data:
        await message.answer("Пользователь не найден")
        await state.clear()
        log.info("Администратор не смог разблокировать поьзователя которого не нашел")
        return
    unban_id = data["user_id"]
    unbanned_already = await db.fetchrow("""SELECT user_id FROM bannedusers WHERE user_id=$1""",unban_id)
    if not unbanned_already:
        await message.answer("Этот пользователь уже разблокирован")
        await state.clear()
        log.info("Администратор не смог разблокировать поьзователя который не был заблокирован %s",unban_id)
        return  
    await db.execute("""DELETE FROM bannedusers WHERE user_id=$1""",unban_id)  
    await message.answer("Пользователь разблокирован")
    log.warning("Администратор разблокировал прользователя %s",unban_id)
    await state.clear()    

@router.message(Razban.username,Command("stop"))
async def stop_fsm3(message:Message,state:FSMContext):
    await state.clear()
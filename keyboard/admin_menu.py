from aiogram.types import ReplyKeyboardMarkup,KeyboardButton

keyboard = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text = "Отправка")],
    [KeyboardButton(text = "Забанить"),KeyboardButton(text = "Разбанить")],
])

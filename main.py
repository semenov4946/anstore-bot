import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = Bot(token=TOKEN)
dp = Dispatcher()


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Айфони в наявності")],
            [KeyboardButton(text="🛠 Сервісний центр")],
            [KeyboardButton(text="🎁 Акції")],
            [KeyboardButton(text="💳 Моя карта лояльності")],
            [KeyboardButton(text="📞 Звʼязок з менеджером")],
        ],
        resize_keyboard=True
    )


@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Вітаємо в Anstore | Apple сервіс та техніка 🍏",
        reply_markup=main_menu()
    )



from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@dp.message(lambda m: m.text == "📱 Айфони в наявності")
async def iphones(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Перейти в канал з наявністю",
                    url="https://t.me/anstore_st"
                )
            ]
        ]
    )

    await message.answer(
        "📱 Актуальна наявність iPhone з фото та цінами 👇",
        reply_markup=keyboard
    )
@dp.message()
async def other_handler(message: Message):
    await message.answer("Розділ у розробці ✍️")
@dp.message(lambda m: m.text == "💳 Моя карта лояльності")
async def loyalty_card(message: Message):
    user_id = message.from_user.id

    await message.answer(
        f"""💳 Ваша карта лояльності ANSTORE

👤 ID: {user_id}
⭐ Статус: Silver
💰 Знижка: 5%

📌 Покажіть це повідомлення менеджеру"""
    )
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

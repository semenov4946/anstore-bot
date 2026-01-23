import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Айфони в наявності")],
            [KeyboardButton(text="🛠 Сервісний центр")],
            [KeyboardButton(text="🎁 Акції")],
            [KeyboardButton(text="💳 Моя карта лояльності")],
            [KeyboardButton(text="📞 Звʼязок з менеджером")]
        ],
        resize_keyboard=True
    )

@dp.message()
async def handler(message):
    if message.text == "/start":
        await message.answer(
            "Вітаємо в Anstore | Apple сервіс та техніка 🍏",
            reply_markup=main_menu()
        )
    else:
        await message.answer("Розділ у розробці 🔧")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

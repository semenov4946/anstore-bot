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

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

CHANNEL_URL = "https://t.me/anstore_st"
MAPS_URL = "https://maps.app.goo.gl/GXY9KfhsVBJyxykv5?g_st=ic"
MANAGER_TG = "https://t.me/anstore_support"
PHONE_URL = "tel:+380634739011"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= MENU =================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Айфони в наявності")],
            [KeyboardButton(text="🎁 Акції")],
            [KeyboardButton(text="📞 Зв'язок з менеджером")],
        ],
        resize_keyboard=True
    )

# ================= START =================
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "🍏 **Anstore** | Apple сервіс та техніка\n\n"
        "Оберіть дію 👇",
        reply_markup=main_menu()
    )

# ================= IPHONES =================
@dp.message(lambda m: m.text == "📱 Айфони в наявності")
async def iphones(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Перейти в канал", url=CHANNEL_URL)]
        ]
    )
    await message.answer(
        "📱 Актуальна наявність iPhone 👇",
        reply_markup=kb
    )

# ================= PROMOTIONS =================
@dp.message(lambda m: m.text == "🎁 Акції")
async def promotions(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Відкрити канал", url=CHANNEL_URL)]
        ]
    )
    await message.answer(
        "🎁 Актуальні акції Anstore 👇\n\n"
        "У каналі натисніть на #акція",
        reply_markup=kb
    )

# ================= CONTACT =================
@dp.message(lambda m: m.text == "📞 Зв'язок з менеджером")
async def contact(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написати в Telegram", url=MANAGER_TG)],
            [InlineKeyboardButton(text="📞 Подзвонити", url=PHONE_URL)],
            [InlineKeyboardButton(text="📍 Адреса магазину", url=MAPS_URL)],
        ]
    )
    await message.answer(
        "📞 Звʼязок з менеджером 👇",
        reply_markup=kb
    )

# ================= RUN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
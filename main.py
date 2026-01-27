import asyncio
import os
import json
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

SHEETS_URL = "https://script.google.com/macros/s/AKfycbzNnZaRw3U99t_jkZibiXBs_Uty3GI1H9-n9HBK3qK0j98N1yWfgSN_NE5rvCY5Qcei/exec"

CHANNEL_URL = "https://t.me/anstore_st"
MAPS_URL = "https://maps.app.goo.gl/GXY9KfhsVBJyxykv5?g_st=ic"
MANAGER_TG = "https://t.me/anstore_support"
PHONE_URL = "tel:+380634739011"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================= MAIN MENU =================
def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Айфони в наявності", url=CHANNEL_URL)],
            [InlineKeyboardButton(text="🎁 Акції", callback_data="promo")],
            [InlineKeyboardButton(text="💳 Моя карта лояльності", callback_data="loyalty")],
            [InlineKeyboardButton(text="📞 Звʼязок з менеджером", callback_data="contact")],
        ]
    )

# ================= HTTP =================
async def get_user(user_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            SHEETS_URL,
            params={"user_id": str(user_id)},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            return json.loads(await resp.text())

# ================= START =================
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "🍏 **Anstore** — Apple сервіс та техніка\n\n"
        "Оберіть розділ 👇",
        reply_markup=main_menu()
    )

# ================= PROMO =================
@dp.callback_query(lambda c: c.data == "promo")
async def promo(cb: CallbackQuery):
    await cb.message.answer(
        "🎁 **Актуальні акції** 👇\n\n"
        "У каналі натисніть на **#акція**, щоб побачити всі пропозиції.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📢 Відкрити канал", url=CHANNEL_URL)]
            ]
        )
    )
    await cb.answer()

# ================= LOYALTY =================
@dp.callback_query(lambda c: c.data == "loyalty")
async def loyalty(cb: CallbackQuery):
    user_id = cb.from_user.id

    try:
        data = await get_user(user_id)
    except Exception:
        data = {"found": False}

    if data.get("found"):
        text = (
            "💳 **Ваша карта лояльності ANSTORE**\n\n"
            f"👤 {data['first_name']} {data['last_name']}\n"
            f"📞 {data['phone']}\n"
            f"⭐ Статус: {data.get('status','Silver')}\n"
            f"💰 Знижка: {data.get('discount',5)}%"
        )
    else:
        text = (
            "ℹ️ Ви ще не зареєстровані в програмі лояльності.\n\n"
            "Зверніться до менеджера — він оформить карту."
        )

    await cb.message.answer(text, reply_markup=main_menu())
    await cb.answer()

# ================= CONTACT =================
@dp.callback_query(lambda c: c.data == "contact")
async def contact(cb: CallbackQuery):
    await cb.message.answer(
        "📞 **Звʼязок з менеджером Anstore** 👇",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💬 Написати в Telegram", url=MANAGER_TG)],
                [InlineKeyboardButton(text="📞 Подзвонити", url=PHONE_URL)],
                [InlineKeyboardButton(text="📍 Адреса магазину", url=MAPS_URL)],
            ]
        )
    )
    await cb.answer()

# ================= RUN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
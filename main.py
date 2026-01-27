import asyncio
import os
import json
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

ADMIN_IDS = {1488727512, 568179276}

SHEETS_URL = "https://script.google.com/macros/s/AKfycbz5oHAJVvLlg7KjeplVMVQQ_ApGzpHNbwinOi2l9ifmMcEFHg3M81Xc_zAzSjmZGs6I/exec"
CHANNEL_URL = "https://t.me/anstore_st"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

SUBSCRIBERS = set()

# ================= STATES =================
class Register(StatesGroup):
    first = State()
    last = State()
    phone = State()

# ================= HELPERS =================
def calc_status(points: int):
    if points >= 50000:
        return "Platinum", 15
    if points >= 25000:
        return "Gold", 10
    if points >= 10000:
        return "Silver", 7
    return "Bronze", 5

# ================= MENU =================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Айфони в наявності")],
            [KeyboardButton(text="🎁 Акції")],
            [KeyboardButton(text="💳 Моя карта лояльності")],
            [KeyboardButton(text="🛠 Сервісний центр")],
            [KeyboardButton(text="📞 Звʼязок з менеджером")],
        ],
        resize_keyboard=True
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

async def save_user(payload: dict):
    async with aiohttp.ClientSession() as session:
        await session.post(
            SHEETS_URL,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=10)
        )

# ================= START =================
@dp.message(Command("start"))
async def start_handler(message: Message):
    SUBSCRIBERS.add(message.chat.id)
    await message.answer(
        "🍏 Anstore | Apple сервіс та техніка\n\n"
        "Оберіть розділ 👇",
        reply_markup=main_menu()
    )

# ================= IPHONES =================
@dp.message(lambda m: m.text == "📱 Айфони в наявності")
async def iphones(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text="📢 Перейти в канал",
            url=CHANNEL_URL
        )]]
    )
    await message.answer("📱 Актуальна наявність iPhone 👇", reply_markup=kb)

# ================= PROMOTIONS =================
@dp.message(lambda m: m.text == "🎁 Акції")
async def promotions(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text="📢 Відкрити канал",
            url=CHANNEL_URL
        )]]
    )
    await message.answer(
        "🎁 Актуальні акції Anstore 👇\n\n"
        "ℹ️ У каналі натисніть на #акція",
        reply_markup=kb
    )

# ================= LOYALTY =================
@dp.message(lambda m: m.text == "💳 Моя карта лояльності")
async def loyalty(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    try:
        data = await get_user(user_id)
    except Exception:
        data = {"found": False}

    if data.get("found"):
        points = int(data.get("points", 0))
        status, discount = calc_status(points)

        await message.answer(
            "💳 Ваша карта лояльності ANSTORE\n\n"
            f"👤 {data['first_name']} {data['last_name']}\n"
            f"📞 {data['phone']}\n"
            f"⭐ Статус: {status}\n"
            f"💰 Знижка: {discount}%\n"
            f"🎯 Бали: {points}",
            reply_markup=main_menu()
        )
    else:
        await message.answer("Введіть ваше імʼя:")
        await state.set_state(Register.first)

@dp.message(Register.first)
async def reg_first(message: Message, state: FSMContext):
    await state.update_data(first=message.text.strip())
    await message.answer("Введіть ваше прізвище:")
    await state.set_state(Register.last)

@dp.message(Register.last)
async def reg_last(message: Message, state: FSMContext):
    await state.update_data(last=message.text.strip())
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Поділитись номером", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Поділіться номером телефону:", reply_markup=kb)
    await state.set_state(Register.phone)

@dp.message(Register.phone)
async def reg_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    await save_user({
        "user_id": str(message.from_user.id),
        "first_name": data["first"],
        "last_name": data["last"],
        "phone": message.contact.phone_number
    })
    await state.clear()
    await message.answer("✅ Карту лояльності створено!", reply_markup=main_menu())

# ================= SERVICE CENTER (FIXED) =================
@dp.message(lambda m: m.text == "🛠 Сервісний центр")
async def service_center(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📞 Звʼязатись з менеджером",
                url="https://t.me/anstore_support"
            )]
        ]
    )
    await message.answer(
        "🛠 **Сервісний центр Anstore**\n\n"
        "• Ремонт iPhone\n"
        "• Заміна дисплею / скла\n"
        "• Заміна акумулятора\n"
        "• Діагностика\n\n"
        "👇 Натисніть кнопку, щоб записатись",
        reply_markup=kb
    )

# ================= CONTACT =================
@dp.message(lambda m: m.text == "📞 Звʼязок з менеджером")
async def contact(message: Message):
    await message.answer(
        "📞 **Звʼязок з менеджером**\n\n"
        "💬 Telegram: https://t.me/anstore_support\n"
        "📞 Телефон: +380634739011\n"
        "📍 Адреса: https://maps.app.goo.gl/GXY9KfhsVBJyxykv5"
    )

# ================= ADMIN SEND =================
@dp.message(Command("send"))
async def admin_send(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if message.photo:
        caption = (message.caption or "").replace("/send", "", 1).strip()
        for chat_id in list(SUBSCRIBERS):
            try:
                await bot.send_photo(chat_id, message.photo[-1].file_id, caption=caption)
            except:
                SUBSCRIBERS.discard(chat_id)
        return

    text = message.text.replace("/send", "", 1).strip()
    if not text:
        return

    for chat_id in list(SUBSCRIBERS):
        try:
            await bot.send_message(chat_id, text)
        except:
            SUBSCRIBERS.discard(chat_id)

# ================= RUN =================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
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

SHEETS_URL = "https://script.google.com/macros/s/AKfycbzNnZaRw3U99t_jkZibiXBs_Uty3GI1H9-n9HBK3qK0j98N1yWfgSN_NE5rvCY5Qcei/exec"

CHANNEL_URL = "https://t.me/anstore_st"
MAPS_URL = "https://maps.app.goo.gl/GXY9KfhsVBJyxykv5?g_st=ic"
MANAGER_TG = "https://t.me/anstore_support"
PHONE_URL = "tel:+380634739011"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================= STATES =================
class Register(StatesGroup):
    first = State()
    last = State()
    phone = State()

# ================= MENU =================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Айфони в наявності")],
            [KeyboardButton(text="🎁 Акції")],
            [KeyboardButton(text="💳 Моя карта лояльності")],
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
    body = json.dumps(payload).encode("utf-8")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            SHEETS_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            print("POST:", await resp.text())

# ================= START =================
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Вітаємо в Anstore | Apple сервіс та техніка 🍏\n\n"
        "Оберіть розділ 👇",
        reply_markup=main_menu()
    )

# ================= IPHONES =================
@dp.message(lambda m: m.text and "Айфони" in m.text)
async def iphones(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Перейти в канал", url=CHANNEL_URL)]
        ]
    )
    await message.answer("📱 Актуальна наявність iPhone 👇", reply_markup=kb)

# ================= PROMOTIONS =================
@dp.message(lambda m: m.text and "Акції" in m.text)
async def promotions(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Відкрити канал", url=CHANNEL_URL)]
        ]
    )
    await message.answer(
        "🎁 Актуальні акції Anstore 👇\n\n"
        "ℹ️ У каналі натисніть на #акція, щоб побачити всі пропозиції.",
        reply_markup=kb
    )

# ================= LOYALTY =================
@dp.message(lambda m: m.text and "карта" in m.text.lower())
async def loyalty(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    try:
        data = await get_user(user_id)
    except Exception:
        data = {"found": False}

    if data.get("found"):
        await message.answer(
            "💳 Ваша карта лояльності ANSTORE\n\n"
            f"👤 {data['first_name']} {data['last_name']}\n"
            f"📞 {data['phone']}\n"
            f"⭐ Статус: {data.get('status','Silver')}\n"
            f"💰 Знижка: {data.get('discount',5)}%",
            reply_markup=main_menu()
        )
    else:
        await message.answer("Введіть ваше ім'я:")
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

# ================= CONTACT (FIXED) =================
@dp.message(lambda m: m.text and "менеджер" in m.text.lower())
async def contact(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написати в Telegram", url=MANAGER_TG)],
            [InlineKeyboardButton(text="📞 Подзвонити", url=PHONE_URL)],
            [InlineKeyboardButton(text="📍 Адреса магазину", url=MAPS_URL)]
        ]
    )
    await message.answer(
        "📞 Звʼязок з менеджером Anstore 👇\n\n"
        "Оберіть зручний спосіб:",
        reply_markup=kb
    )

# ================= FALLBACK =================
@dp.message()
async def fallback(message: Message):
    await message.answer("Оберіть пункт з меню 👇", reply_markup=main_menu())

# ================= RUN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
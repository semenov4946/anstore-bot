import asyncio
import os
import requests
import json

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

# ========= CONFIG =========
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

SHEETS_URL = "https://script.google.com/macros/s/AKfycbwNtUxaz8gOA5_NLyQqV36xJomeR21iIVjZ1TbbBDc0IdVTMHkKZin2b17GI9empcOQ/exec"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ========= STATES =========
class Register(StatesGroup):
    first = State()
    last = State()
    phone = State()

# ========= MENU =========
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Айфони в наявності")],
            [KeyboardButton(text="🛠 Сервісний центр")],
            [KeyboardButton(text="🎁 Акції")],
            [KeyboardButton(text="💳 Моя карта лояльності")],
            [KeyboardButton(text="📞 Зв'язок з менеджером")],
        ],
        resize_keyboard=True
    )

# ========= START =========
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Вітаємо в Anstore | Apple сервіс та техніка 🍏",
        reply_markup=main_menu()
    )

# ========= IPHONES =========
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
        "📱 Актуальна наявність iPhone 👇",
        reply_markup=keyboard
    )

# ========= LOYALTY CARD =========
@dp.message(lambda m: m.text == "💳 Моя карта лояльності")
async def loyalty_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    try:
        r = requests.get(
            SHEETS_URL,
            params={"user_id": user_id},
            timeout=10
        )
        data = json.loads(r.text)
    except Exception:
        data = {"found": False}

    if data.get("found") is True:
        text = (
            "💳 Ваша карта лояльності ANSTORE\n\n"
            f"👤 {data.get('first_name')} {data.get('last_name')}\n"
            f"📞 {data.get('phone')}\n"
            "⭐ Статус: Silver\n"
            "💰 Знижка: 5%"
        )
        await message.answer(text, reply_markup=main_menu())
    else:
        await message.answer("Введіть ваше ім'я:")
        await state.set_state(Register.first)

@dp.message(Register.first)
async def reg_first(message: Message, state: FSMContext):
    await state.update_data(first=message.text)
    await message.answer("Введіть ваше прізвище:")
    await state.set_state(Register.last)

@dp.message(Register.last)
async def reg_last(message: Message, state: FSMContext):
    await state.update_data(last=message.text)

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

    requests.post(
        SHEETS_URL,
        json={
            "user_id": message.from_user.id,
            "first_name": data["first"],
            "last_name": data["last"],
            "phone": message.contact.phone_number
        },
        timeout=10
    )

    await state.clear()
    await message.answer("✅ Карту лояльності створено!", reply_markup=main_menu())

# ========= OTHER =========
@dp.message(lambda m: m.text in ["🛠 Сервісний центр", "🎁 Акції", "📞 Зв'язок з менеджером"])
async def other_sections(message: Message):
    await message.answer("Розділ у розробці 🛠")

@dp.message()
async def fallback(message: Message):
    await message.answer("Оберіть пункт з меню 👇", reply_markup=main_menu())

# ========= RUN =========
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

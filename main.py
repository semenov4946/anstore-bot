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

MANAGER_TG = "https://t.me/anstore_support"
PHONE_NUMBER = "0634739011"
MAP_URL = "https://maps.app.goo.gl/6zkS8iwpShFFTpEN6"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

SUBSCRIBERS = set()

# ================= STATES =================
class Register(StatesGroup):
    first = State()
    last = State()
    phone = State()

# ================= LEVELS =================
LEVELS = [
    ("Bronze", 0, 5),
    ("Silver", 10000, 7),
    ("Gold", 25000, 10),
    ("Platinum", 50000, 15),
]

def get_level(points: int):
    current = LEVELS[0]
    next_level = None
    for lvl in LEVELS:
        if points >= lvl[1]:
            current = lvl
        else:
            next_level = lvl
            break
    return current, next_level

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
        "🍏 Anstore | Apple сервіс та техніка\n\nОберіть розділ 👇",
        reply_markup=main_menu()
    )

# ================= CONTACT =================
@dp.message(lambda m: m.text == "📞 Звʼязок з менеджером")
async def contact(message: Message):
    await message.answer(
        "📞 Звʼязок з Anstore\n\n"
        f"💬 Telegram:\n{MANAGER_TG}\n\n"
        f"📞 Телефон:\n{PHONE_NUMBER}\n\n"
        f"📍 Магазин на карті:\n{MAP_URL}"
    )

# ================= ADMIN SEND (TEXT) =================
@dp.message(Command("send"))
async def admin_send_text(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    text = message.text.replace("/send", "", 1).strip()
    if not text:
        await message.answer("❗ Напишіть текст після /send")
        return

    sent = 0
    for chat_id in list(SUBSCRIBERS):
        try:
            await bot.send_message(chat_id, text)
            sent += 1
        except:
            SUBSCRIBERS.discard(chat_id)

    await message.answer(f"✅ Розіслано: {sent}")

# ================= ADMIN SEND (PHOTO + TEXT) =================
@dp.message(lambda m: m.photo and m.caption and m.caption.startswith("/send"))
async def admin_send_photo(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    caption = message.caption.replace("/send", "", 1).strip()
    sent = 0

    for chat_id in list(SUBSCRIBERS):
        try:
            await bot.send_photo(
                chat_id,
                message.photo[-1].file_id,
                caption=caption
            )
            sent += 1
        except:
            SUBSCRIBERS.discard(chat_id)

    await message.answer(f"✅ Фото + текст розіслано: {sent}")

# ================= RUN =================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
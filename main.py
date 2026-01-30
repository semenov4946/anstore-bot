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
    InlineKeyboardButton,
    InputMediaPhoto
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

# ================= BOT =================
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

# ================= FORWARD FROM CHANNEL (AUTO POSTING) =================
albums = {}

@dp.message(lambda m: m.forward_from_chat)
async def forward_from_channel(message: Message):
    # тільки адміни
    if message.from_user.id not in ADMIN_IDS:
        return

    # ===== АЛЬБОМ =====
    if message.media_group_id:
        gid = message.media_group_id
        albums.setdefault(gid, []).append(message)

        await asyncio.sleep(1)

        if gid not in albums:
            return

        messages = albums.pop(gid)

        media = []
        caption = messages[0].caption or ""

        for i, m in enumerate(messages):
            media.append(
                InputMediaPhoto(
                    media=m.photo[-1].file_id,
                    caption=caption if i == 0 else None
                )
            )

        for chat_id in list(SUBSCRIBERS):
            try:
                await bot.send_media_group(chat_id, media)
            except:
                SUBSCRIBERS.discard(chat_id)

        return

    # ===== ОДНЕ ФОТО =====
    if message.photo:
        for chat_id in list(SUBSCRIBERS):
            try:
                await bot.send_photo(
                    chat_id,
                    message.photo[-1].file_id,
                    caption=message.caption or ""
                )
            except:
                SUBSCRIBERS.discard(chat_id)
        return

    # ===== ТІЛЬКИ ТЕКСТ =====
    if message.text:
        for chat_id in list(SUBSCRIBERS):
            try:
                await bot.send_message(chat_id, message.text)
            except:
                SUBSCRIBERS.discard(chat_id)

# ================= IPHONES =================
@dp.message(lambda m: m.text == "📱 Айфони в наявності")
async def iphones(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📢 Перейти в канал", url=CHANNEL_URL)]]
    )
    await message.answer("📱 Актуальна наявність iPhone 👇", reply_markup=kb)

# ================= PROMOTIONS =================
@dp.message(lambda m: m.text == "🎁 Акції")
async def promotions(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📢 Відкрити канал", url=CHANNEL_URL)]]
    )
    await message.answer(
        "🎁 Актуальні акції Anstore 👇\n\nℹ️ У каналі натисніть на #акція",
        reply_markup=kb
    )

# ================= LOYALTY =================
@dp.message(lambda m: m.text == "💳 Моя карта лояльності")
async def loyalty(message: Message, state: FSMContext):
    await state.clear()

    try:
        data = await get_user(message.from_user.id)
    except:
        data = {"found": False}

    if not data.get("found"):
        await message.answer("✍️ Введіть ваше імʼя:")
        await state.set_state(Register.first)
        return

    points = int(data.get("points", 0))
    current, next_level = get_level(points)

    text = (
        "💳 Ваша карта лояльності ANSTORE\n\n"
        f"👤 {data['first_name']} {data['last_name']}\n"
        f"📞 {data['phone']}\n\n"
        f"🏷 Статус: {current[0]}\n"
        f"💰 Знижка: {current[2]}%\n"
        f"🎯 Бали: {points} грн\n"
    )

    if next_level:
        text += f"\n⬆️ До рівня {next_level[0]}: {next_level[1] - points} грн"
    else:
        text += "\n🏆 Максимальний рівень досягнуто"

    await message.answer(text, reply_markup=main_menu())

# ================= SERVICE CENTER =================
@dp.message(lambda m: m.text == "🛠 Сервісний центр")
async def service_center(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📍 Ми на карті", url=MAP_URL)],
            [InlineKeyboardButton(text="💬 Записатись", url=MANAGER_TG)]
        ]
    )
    await message.answer(
        "🛠 Сервісний центр Anstore\n\n"
        "• Ремонт iPhone\n"
        "• Заміна дисплею / скла\n"
        "• Заміна акумулятора\n"
        "• Діагностика",
        reply_markup=kb
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

# ================= RUN =================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
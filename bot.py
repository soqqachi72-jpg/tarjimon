import asyncio, json, os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "8296490006:AAE7ikwvPuyCaTVk3_DYZXH6iXYr2kdHh4g"
ADMIN_ID = 6073024030
CHANNEL = "@seen_sms"
WEBAPP = "https://soqqachi72-jpg.github.io/tarjimon/"
USERS_FILE = "users.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return set(json.load(f))
    return set()

def save_users(u):
    with open(USERS_FILE, "w") as f:
        json.dump(list(u), f)

def add_user(uid):
    u = load_users()
    u.add(uid)
    save_users(u)

async def is_sub(uid):
    try:
        m = await bot.get_chat_member(CHANNEL, uid)
        return m.status not in ("left", "kicked", "banned")
    except:
        return False

def sub_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 @seen_sms ga obuna bo'lish", url="https://t.me/seen_sms"))
    kb.add(InlineKeyboardButton("✅ Obuna bo'ldim", callback_data="check"))
    return kb

def app_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🌐 Tarjimonni ochish", web_app=WebAppInfo(url=WEBAPP)))
    return kb

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    add_user(msg.from_user.id)
    if await is_sub(msg.from_user.id):
        await msg.answer("👋 Xush kelibsiz!\n\n✅ Obuna tasdiqlandi.\n\nTarjimonni oching 👇", reply_markup=app_kb())
    else:
        await msg.answer("🔒 Botdan foydalanish uchun\n<b>@seen_sms</b> ga obuna bo'ling!\n\nObuna bo'lgach ✅ bosing.", parse_mode="HTML", reply_markup=sub_kb())

@dp.callback_query_handler(text="check")
async def check(cb: types.CallbackQuery):
    if await is_sub(cb.from_user.id):
        await cb.message.edit_text("✅ Obuna tasdiqlandi!\n\nTarjimonni oching 👇", reply_markup=app_kb())
    else:
        await cb.answer("⚠️ Hali obuna bo'lmagansiz!", show_alert=True)

@dp.message_handler(commands=["admin"])
async def admin(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    u = load_users()
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("👥 Obunachi soni", callback_data="count"))
    kb.add(InlineKeyboardButton("📨 Hammaga xabar", callback_data="broadcast"))
    await msg.answer(f"🛠 Admin panel\n\n👥 Jami: {len(u)} ta", reply_markup=kb)

@dp.callback_query_handler(text="count")
async def count(cb: types.CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.answer(f"👥 Jami: {len(load_users())} ta", show_alert=True)

broadcast_mode = False

@dp.callback_query_handler(text="broadcast")
async def bcast_start(cb: types.CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    global broadcast_mode
    broadcast_mode = True
    await cb.message.answer("📨 Xabarni yozing:")
    await cb.answer()

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and broadcast_mode and not m.text.startswith("/"))
async def bcast(msg: types.Message):
    global broadcast_mode
    broadcast_mode = False
    u = load_users()
    sent = 0
    for uid in u:
        try:
            await bot.send_message(uid, msg.text)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await msg.answer(f"✅ Yuborildi: {sent} ta")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

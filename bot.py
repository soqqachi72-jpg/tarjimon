import asyncio, json, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN  = "8296490006:AAE7ikwvPuyCaTVk3_DYZXH6iXYr2kdHh4g"
ADMIN_ID   = 6073024030
CHANNEL    = "@seen_sms"
WEBAPP     = "https://soqqachi72-jpg.github.io/tarjimon/"
USERS_FILE = "users.json"

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

# ── Foydalanuvchilarni saqlash ──
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

def add_user(uid):
    users = load_users()
    users.add(uid)
    save_users(users)

# ── Obuna tekshirish ──
async def is_subscribed(user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(CHANNEL, user_id)
        return m.status not in ("left", "kicked", "banned")
    except:
        return False

# ── Klaviaturalar ──
def sub_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 @seen_sms ga obuna bo'lish",
                              url="https://t.me/seen_sms")],
        [InlineKeyboardButton(text="✅ Obuna bo'ldim — tekshirish",
                              callback_data="check")]
    ])

def app_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Tarjimonni ochish",
                              web_app=WebAppInfo(url=WEBAPP))]
    ])

# ── /start ──
@dp.message(CommandStart())
async def start(msg: types.Message):
    add_user(msg.from_user.id)
    if await is_subscribed(msg.from_user.id):
        await msg.answer(
            "👋 Xush kelibsiz!\n\n"
            "✅ Obuna tasdiqlandi.\n\n"
            "Quyidagi tugmani bosib tarjimonni oching 👇",
            reply_markup=app_kb()
        )
    else:
        await msg.answer(
            "🔒 Botdan foydalanish uchun\n"
            "<b>@seen_sms</b> kanaliga obuna bo'ling!\n\n"
            "Obuna bo'lgach ✅ tugmasini bosing.",
            parse_mode="HTML",
            reply_markup=sub_kb()
        )

# ── Obuna tekshirish callback ──
@dp.callback_query(F.data == "check")
async def check(cb: types.CallbackQuery):
    if await is_subscribed(cb.from_user.id):
        await cb.message.edit_text(
            "✅ Obuna tasdiqlandi!\n\nTarjimonni oching 👇",
            reply_markup=app_kb()
        )
    else:
        await cb.answer("⚠️ Siz hali obuna bo'lmagansiz!", show_alert=True)

# ── ADMIN PANEL ──
@dp.message(Command("admin"))
async def admin_panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    users = load_users()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Obunachi soni", callback_data="count")],
        [InlineKeyboardButton(text="📨 Hammaga xabar yuborish", callback_data="broadcast")],
    ])
    await msg.answer(
        f"🛠 <b>Admin panel</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{len(users)}</b>",
        parse_mode="HTML",
        reply_markup=kb
    )

@dp.callback_query(F.data == "count")
async def count_users(cb: types.CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    users = load_users()
    await cb.answer(f"👥 Jami: {len(users)} ta foydalanuvchi", show_alert=True)

@dp.callback_query(F.data == "broadcast")
async def broadcast_start(cb: types.CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    await cb.message.answer(
        "📨 Hammaga yuboriladigan xabarni yozing:\n\n"
        "(Bekor qilish uchun /admin)"
    )
    await cb.answer()

# Broadcast xabarini qabul qilish
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_broadcast(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    users = load_users()
    sent = 0
    failed = 0
    status_msg = await msg.answer("📨 Xabar yuborilmoqda...")
    for uid in users:
        try:
            await bot.send_message(uid, msg.text)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    await status_msg.edit_text(
        f"✅ Xabar yuborildi!\n\n"
        f"✔️ Muvaffaqiyatli: {sent}\n"
        f"❌ Yuborilmadi: {failed}"
    )

async def main():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# bot/main.py

import asyncio
import logging
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config, validate_config
from motor.motor_asyncio import AsyncIOMotorClient

# ─── BASIC LOGGING ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ─── VALIDATE CONFIG ──────────────────────────────────────────────────
validate_config()

# ─── DATABASE ─────────────────────────────────────────────────────────
mongo = AsyncIOMotorClient(Config.DATABASE_URL)
db = mongo["filefucker"]

users_col = db["users"]
admins_col = db["admins"]

# ─── BOT CLIENT ───────────────────────────────────────────────────────
app = Client(
    name="FileFucker",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=50,
    in_memory=True
)

# ─── HELPERS ──────────────────────────────────────────────────────────
def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMINS


async def get_user(user_id: int):
    return await users_col.find_one({"user_id": user_id})


async def add_user(user_id: int, username: str | None):
    user = await get_user(user_id)
    if not user:
        await users_col.insert_one({
            "user_id": user_id,
            "username": username,
            "is_premium": False,
            "premium_expiry": None,
            "language": Config.DEFAULT_LANGUAGE,
            "banned": False,
            "joined_at": datetime.utcnow()
        })


async def send_log(text: str):
    try:
        await app.send_message(Config.LOG_CHANNEL, text)
    except Exception as e:
        logger.error(f"Log send failed: {e}")


def hacker_log(title: str, body: str) -> str:
    return f"""
🛑 {title}
━━━━━━━━━━━━━━━━━━
{body}
🕒 Time: {datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC
━━━━━━━━━━━━━━━━━━
"""


# ─── START EVENT ──────────────────────────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_handler(_, message):
    user = message.from_user
    await add_user(user.id, user.username)

    text = (
        "👋 **Welcome to FileFucker**\n\n"
        "This is a controlled-access file system.\n\n"
        "💎 Premium users get **direct files**.\n"
        "🧨 Free users go through **secured delivery layers**.\n\n"
        "Use /profile to check your status.\n"
        "Use /language to change language."
    )

    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("👤 My Profile", callback_data="profile")]]
        )
    )

    log_text = hacker_log(
        "NEW USER CONNECTED",
        f"👤 User: @{user.username}\n🆔 ID: {user.id}\n⚠️ Access Level: FREE"
    )
    await send_log(log_text)


# ─── PROFILE ──────────────────────────────────────────────────────────
@app.on_message(filters.command("profile") & filters.private)
async def profile_handler(_, message):
    user = await get_user(message.from_user.id)

    premium_status = "✅ YES" if user["is_premium"] else "❌ NO"
    expiry = user["premium_expiry"] or "N/A"

    text = (
        "👤 **Your Profile**\n\n"
        f"🆔 ID: `{user['user_id']}`\n"
        f"💎 Premium: {premium_status}\n"
        f"⏳ Expiry: {expiry}\n"
        f"🌐 Language: {user['language']}"
    )

    await message.reply_text(text)


# ─── LANGUAGE ─────────────────────────────────────────────────────────
@app.on_message(filters.command("language") & filters.private)
async def language_handler(_, message):
    await message.reply_text(
        "🌐 Choose your language:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
                InlineKeyboardButton("🇮🇳 Hinglish", callback_data="lang_hi")
            ]
        ])
    )


@app.on_callback_query(filters.regex("^lang_"))
async def set_language(_, query):
    lang = query.data.split("_")[1]
    await users_col.update_one(
        {"user_id": query.from_user.id},
        {"$set": {"language": lang}}
    )
    await query.answer("Language updated ✅", show_alert=True)


# ─── ADMIN: ADD PREMIUM ───────────────────────────────────────────────
@app.on_message(filters.command("addpremium") & filters.private)
async def add_premium(_, message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 3:
        return await message.reply_text("Usage: /addpremium user_id 7d|30d|365d")

    user_id = int(parts[1])
    plan = parts[2]

    if plan not in Config.PREMIUM_PLANS:
        return await message.reply_text("Invalid plan")

    days = Config.PREMIUM_PLANS[plan]["days"]
    expiry = datetime.utcnow().date().isoformat()

    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {
            "is_premium": True,
            "premium_expiry": expiry
        }}
    )

    await message.reply_text("✅ Premium activated")

    log_text = hacker_log(
        "PRIVILEGED ACCESS GRANTED",
        f"👑 Admin: {message.from_user.id}\n"
        f"👤 Target User: {user_id}\n"
        f"⏳ Duration: {days} days"
    )
    await send_log(log_text)


# ─── BOT STARTUP ──────────────────────────────────────────────────────
async def main():
    await app.start()
    me = await app.get_me()

    start_log = hacker_log(
        "SYSTEM ONLINE",
        f"🤖 Bot: @{me.username}\n"
        f"🚀 Version: {Config.VERSION}\n"
        f"🧠 Mode: MONITORING ACTIVE"
    )
    await send_log(start_log)

    logger.info("FileFucker bot started")
    await idle()


from pyrogram.idle import idle

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

# bot/main.py

import asyncio
import logging
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config, validate_config
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.services.premium import calculate_expiry, is_expired

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

# ─── BOT CLIENT ───────────────────────────────────────────────────────
app = Client(
    name="FileFucker",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=50,
    in_memory=True
)

# ─── SCHEDULER ────────────────────────────────────────────────────────
scheduler = AsyncIOScheduler()


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


# ─── PREMIUM EXPIRY CHECK ──────────────────────────────────────────────
async def check_premium_expiry():
    async for user in users_col.find({"is_premium": True}):
        if is_expired(user.get("premium_expiry")):
            await users_col.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"is_premium": False, "premium_expiry": None}}
            )

            try:
                await app.send_message(
                    user["user_id"],
                    "😬 Bhai tera **Premium expire ho gaya**.\n\n"
                    "Ab free mode active hai.\n"
                    "Dobara premium lega to seedha files milengi 😎"
                )
            except:
                pass

            log_text = hacker_log(
                "ACCESS REVOKED",
                f"👤 User: {user.get('username')}\n"
                f"🆔 ID: {user['user_id']}\n"
                f"⚠️ Reason: PREMIUM EXPIRED"
            )
            await send_log(log_text)


# ─── START ────────────────────────────────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_handler(_, message):
    user = message.from_user
    await add_user(user.id, user.username)

    await message.reply_text(
        "👋 **Welcome to FileFucker**\n\n"
        "💎 Premium = Direct files\n"
        "🧨 Free = Secure delivery layers\n\n"
        "Use /profile to check status."
    )

    await send_log(
        hacker_log(
            "NEW USER CONNECTED",
            f"👤 User: @{user.username}\n🆔 ID: {user.id}\n⚠️ Access: FREE"
        )
    )


# ─── PROFILE ──────────────────────────────────────────────────────────
@app.on_message(filters.command("profile") & filters.private)
async def profile_handler(_, message):
    user = await get_user(message.from_user.id)

    text = (
        "👤 **Your Profile**\n\n"
        f"🆔 ID: `{user['user_id']}`\n"
        f"💎 Premium: {'YES' if user['is_premium'] else 'NO'}\n"
        f"⏳ Expiry: {user['premium_expiry'] or 'N/A'}"
    )

    await message.reply_text(text)


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
    expiry = calculate_expiry(days)

    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"is_premium": True, "premium_expiry": expiry}}
    )

    await message.reply_text("✅ Premium activated")

    await send_log(
        hacker_log(
            "PRIVILEGED ACCESS GRANTED",
            f"👑 Admin: {message.from_user.id}\n"
            f"👤 Target: {user_id}\n"
            f"⏳ Expiry: {expiry}"
        )
    )


# ─── BOT STARTUP ──────────────────────────────────────────────────────
async def main():
    await app.start()

    scheduler.add_job(check_premium_expiry, "interval", hours=24)
    scheduler.start()

    me = await app.get_me()
    await send_log(
        hacker_log(
            "SYSTEM ONLINE",
            f"🤖 Bot: @{me.username}\n"
            f"🚀 Version: {Config.VERSION}\n"
            f"🧠 Premium Watchdog: ACTIVE"
        )
    )

    logger.info("Bot started")
    await idle()


from pyrogram.idle import idle

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

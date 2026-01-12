# bot/main.py

import asyncio
import logging

from pyrogram import Client, idle
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import Config, validate_config

# ─── HANDLERS ─────────────────────────────────────────────────────────
from bot.handlers.start import register_start_handler
from bot.handlers.ping import register_ping_handler   # ✅ DEBUG LIFELINE
from bot.handlers.file import register_file_handler
from bot.handlers.genlink import register_genlink_handler
from bot.handlers.link import register_link_handler
from bot.handlers.wait import register_wait_handler
from bot.handlers.request import register_request_handler
from bot.handlers.stats import register_stats_handlers
from bot.handlers.premium import register_premium_handlers
from bot.handlers.profile import register_profile_handler
from bot.handlers.language import register_language_handler

# ─── SERVICES ─────────────────────────────────────────────────────────
from bot.services.premium import is_expired
from bot.services.logs import send_log, log_system_online


# ─── LOGGING ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ─── CONFIG VALIDATION ────────────────────────────────────────────────
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
    workers=20,
    in_memory=True
)


# ─── SCHEDULER ────────────────────────────────────────────────────────
scheduler = AsyncIOScheduler()


# ─── PREMIUM EXPIRY WATCHDOG ──────────────────────────────────────────
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
                    "⏰ **Premium Expired**\n\n"
                    "Free mode active ho gaya hai.\n"
                    "Dobara premium lega to direct files milengi 😎"
                )
            except Exception:
                pass


# ─── REGISTER ALL HANDLERS ────────────────────────────────────────────
def register_all_handlers():
    # 🔥 BASIC LIFELINE (sabse pehle)
    register_ping_handler(app)

    # core user flow
    register_start_handler(app, users_col)
    register_file_handler(app, db, users_col)
    register_genlink_handler(app, db, users_col)

    # ⚠️ start payload / wait flow
    register_link_handler(app, db, users_col)
    register_wait_handler(app, db, users_col)

    # user utilities
    register_profile_handler(app, users_col)
    register_language_handler(app, users_col)
    register_request_handler(app, users_col)

    # admin / analytics
    register_stats_handlers(app, db, users_col)
    register_premium_handlers(app, users_col)


# ─── MAIN ─────────────────────────────────────────────────────────────
async def main():
    await app.start()

    register_all_handlers()

    scheduler.add_job(check_premium_expiry, "interval", hours=24)
    scheduler.start()

    me = await app.get_me()
    await send_log(
        app,
        log_system_online(
            bot_username=me.username,
            version=Config.VERSION
        )
    )

    logger.info("🔥 FileFucker fully started & production ready")
    await idle()


# ─── ENTRY POINT (HEROKU / VPS SAFE) ───────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())

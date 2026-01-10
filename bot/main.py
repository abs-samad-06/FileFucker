# bot/main.py

import asyncio
import logging
from datetime import datetime

from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import Config, validate_config

# Services
from bot.services.premium import calculate_expiry, is_expired
from bot.services.logs import send_log, log_system_online
from bot.services.security import ban_payload, unban_payload

# Handlers (register functions)
from bot.handlers.link import register_link_handler
from bot.handlers.stats import register_stats_handlers
from bot.handlers.users import register_user_list_handlers
from bot.handlers.request import register_request_handler

# ─── LOGGING ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ─── CONFIG CHECK ─────────────────────────────────────────────────────
validate_config()

# ─── DB ───────────────────────────────────────────────────────────────
mongo = AsyncIOMotorClient(Config.DATABASE_URL)
db = mongo["filefucker"]
users_col = db["users"]

# ─── BOT ──────────────────────────────────────────────────────────────
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
                    "😬 Premium expire ho gaya.\nFree mode active hai.\n"
                    "Dobara premium lega to seedha files milengi 😎"
                )
            except:
                pass


# ─── REGISTER HANDLERS ────────────────────────────────────────────────
def register_all():
    register_link_handler(app, db, users_col)
    register_stats_handlers(app, db, users_col)
    register_user_list_handlers(app, users_col)
    register_request_handler(app, users_col)


# ─── STARTUP ──────────────────────────────────────────────────────────
async def main():
    await app.start()
    register_all()

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

    logger.info("FileFucker fully assembled & running")
    await idle()


from pyrogram.idle import idle

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

# bot/main.py

import asyncio
import logging

from pyrogram import Client
from pyrogram import idle
from motor.motor_asyncio import AsyncIOMotorClient

from config import Config, validate_config
from bot.handlers.start import register_start_handler


# ─── LOGGING ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ─── CONFIG CHECK ─────────────────────────────────────────────────────
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
    workers=10,
    in_memory=True
)


# ─── MAIN ─────────────────────────────────────────────────────────────
async def main():
    await app.start()

    register_start_handler(app, users_col)

    logger.info("🔥 FileFucker started & ready")
    await idle()


# ─── ENTRY POINT (HEROKU SAFE) ────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())

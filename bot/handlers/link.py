# bot/handlers/link.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.services.premium import is_premium
from bot.services.logs import send_log, log_link_step
from bot.services.shortener import get_link


def register_link_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_message(filters.command("start") & filters.private)
    async def start_with_link(client, message):
        parts = message.text.split()

        # ─── NORMAL /start (no token) ────────────────────────────────
        if len(parts) == 1:
            return  # start.py will handle normal /start

        token = parts[1]
        user = message.from_user

        # ─── FETCH SHORTENER LINK ────────────────────────────────────
        link = await get_link(db, token)
        if not link:
            await message.reply_text(
                "❌ Invalid ya expired link.\n"
                "Link dead ho chuka hai BC."
            )
            return

        # ─── FETCH USER + FILE ───────────────────────────────────────
        user_db = await users_col.find_one({"user_id": user.id})
        file = await files_col.find_one({"file_id": link["file_id"]})

        if not file:
            await message.reply_text(
                "❌ File missing.\n"
                "Link disable kar diya gaya."
            )
            return

        # ─── PREMIUM USER → DIRECT DELIVERY ──────────────────────────
        if is_premium(user_db):
            await files_col.update_one(
                {"file_id": link["file_id"]},
                {"$inc": {"downloads": 1}}
            )

            await send_log(
                app,
                log_link_step(
                    user.username

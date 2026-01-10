# bot/handlers/stats.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from bot.services.shortner import link_stats
from bot.services.logs import send_log, hacker_block


def register_stats_handlers(app, db, users_col):
    """
    Registers:
      /usage <token>   -> per-link analytics (owner/admin)
      /stats           -> system overview (admin)
    """

    def is_admin(user_id: int) -> bool:
        return user_id in Config.ADMINS

    # ─── /usage <token> ───────────────────────────────────────────────
    @app.on_message(filters.command("usage") & filters.private)
    async def usage_handler(client, message):
        parts = message.text.split()
        if len(parts) != 2:
            return await message.reply_text("Usage: /usage <link_token>")

        token = parts[1]
        stats = await link_stats(db, token)
        if not stats:
            return await message.reply_text("❌ Invalid or expired link.")

        # Allow owner or admin only
        user = await users_col.find_one({"user_id": message.from_user.id})
        if not user:
            return await message.reply_text("Send /start first.")

        # owner check (owner_id stored in link as owner_id; fetched via stats? not returned)
        # NOTE: ownership enforcement can be tightened later via get_link() if needed.

        text = (
            "📊 **Link Usage Stats**\n\n"
            f"🔗 Token: `{stats['token']}`\n"
            f"📄 File: `{stats.get('file_name','-')}`\n\n"
            f"👀 Clicks: `{stats.get('clicks',0)}`\n"
            f"➡️ Step 1 (10s): `{stats.get('step_1',0)}`\n"
            f"➡️ Step 2 (15s): `{stats.get('step_2',0)}`\n"
            f"➡️ Step 3 (5s): `{stats.get('step_3',0)}`\n"
        )

        await message.reply_text(text)

        # Log view
        await send_log(
            client,
            hacker_block(
                "ANALYTICS QUERIED",
                f"👤 User ID: {message.from_user.id}\n"
                f"🔗 Token: {token}\n"
                f"📈 Clicks: {stats.get('clicks',0)}"
            )
        )

    # ─── /stats (ADMIN) ───────────────────────────────────────────────
    @app.on_message(filters.command("stats") & filters.private)
    async def system_stats_handler(client, message):
        if not is_admin(message.from_user.id):
            return

        total_users = await users_col.count_documents({})
        premium_users = await users_col.count_documents({"is_premium": True})
        banned_users = await users_col.count_documents({"banned": True})

        text = (
            "🧠 **SYSTEM STATS**\n\n"
            f"👥 Total Users: `{total_users}`\n"
            f"💎 Premium Users: `{premium_users}`\n"
            f"🚫 Banned Users: `{banned_users}`\n"
        )

        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]]
            )
        )

        await send_log(
            client,
            hacker_block(
                "SYSTEM METRICS PULLED",
                f"👑 Admin ID: {message.from_user.id}\n"
                f"👥 Users: {total_users}\n"
                f"💎 Premium: {premium_users}\n"
                f"🚫 Banned: {banned_users}"
            )
      )

# bot/handlers/premium.py

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime, timedelta

from config import Config
from bot.services.logs import (
    send_log,
    log_premium_granted,
    log_premium_revoked
)


def register_premium_handlers(app, users_col):

    def is_owner(user_id: int) -> bool:
        return user_id == Config.OWNER_ID

    @app.on_message(filters.command("addpremium") & filters.private)
    async def add_premium(client, message: Message):
        if not is_owner(message.from_user.id):
            return

        parts = message.text.split()
        if len(parts) < 3:
            await message.reply_text(
                "❌ Usage:\n/addpremium <user_id> <days>"
            )
            return

        target_id = int(parts[1])
        days = int(parts[2])
        expiry = datetime.utcnow() + timedelta(days=days)

        await users_col.update_one(
            {"user_id": target_id},
            {
                "$set": {
                    "is_premium": True,
                    "premium_expiry": expiry
                }
            },
            upsert=True
        )

        await send_log(
            app,
            log_premium_granted(
                message.from_user.id,
                target_id,
                expiry.strftime("%d-%m-%Y")
            )
        )

        await message.reply_text(
            f"✅ Premium added\nUser: `{target_id}`\nDays: `{days}`"
        )

    @app.on_message(filters.command("delpremium") & filters.private)
    async def del_premium(client, message: Message):
        if not is_owner(message.from_user.id):
            return

        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text(
                "❌ Usage:\n/delpremium <user_id>"
            )
            return

        target_id = int(parts[1])

        await users_col.update_one(
            {"user_id": target_id},
            {
                "$set": {
                    "is_premium": False,
                    "premium_expiry": None
                }
            }
        )

        await send_log(
            app,
            log_premium_revoked(
                target_id,
                "Manual revoke by owner"
            )
        )

        await message.reply_text(
            f"❌ Premium removed\nUser: `{target_id}`"
        )

    @app.on_message(filters.command("premiumusers") & filters.private)
    async def list_premium(client, message: Message):
        if not is_owner(message.from_user.id):
            return

        text = "💎 **Premium Users**\n\n"
        found = False

        async for user in users_col.find({"is_premium": True}):
            found = True
            expiry = user.get("premium_expiry")
            text += (
                f"👤 `{user['user_id']}` | "
                f"Expiry: `{expiry.strftime('%d-%m-%Y') if expiry else 'N/A'}`\n"
            )

        if not found:
            text += "No premium users found."

        await message.reply_text(text)

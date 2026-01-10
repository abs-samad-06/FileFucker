# bot/handlers/premium.py

from pyrogram import filters
from bot.services.premium import calculate_expiry
from config import Config


def register_premium_handlers(app, users_col):

    def is_admin(user_id: int) -> bool:
        return user_id == Config.OWNER_ID

    @app.on_message(filters.command("addpremium") & filters.private)
    async def add_premium(client, message):
        if not is_admin(message.from_user.id):
            return

        if len(message.command) < 3:
            await message.reply_text(
                "❌ Usage:\n/addpremium user_id days"
            )
            return

        user_id = int(message.command[1])
        days = int(message.command[2])

        expiry = calculate_expiry(days)

        await users_col.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "is_premium": True,
                    "premium_expiry": expiry
                }
            },
            upsert=True
        )

        await message.reply_text(
            f"✅ Premium added\nUser: `{user_id}`\nDays: `{days}`"
        )

    @app.on_message(filters.command("delpremium") & filters.private)
    async def del_premium(client, message):
        if not is_admin(message.from_user.id):
            return

        if len(message.command) < 2:
            await message.reply_text(
                "❌ Usage:\n/delpremium user_id"
            )
            return

        user_id = int(message.command[1])

        await users_col.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "is_premium": False,
                    "premium_expiry": None
                }
            }
        )

        await message.reply_text(
            f"❌ Premium removed\nUser: `{user_id}`"
        )

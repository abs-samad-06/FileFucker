# bot/handlers/users.py

from pyrogram import filters
from config import Config
from bot.services.logs import send_log, hacker_block


def register_user_list_handlers(app, users_col):
    """
    Registers:
      /users          -> all users (admin)
      /premiumusers   -> premium users (admin)
    """

    def is_admin(user_id: int) -> bool:
        return user_id in Config.ADMINS

    # ─── /users ───────────────────────────────────────────────────────
    @app.on_message(filters.command("users") & filters.private)
    async def users_handler(client, message):
        if not is_admin(message.from_user.id):
            return

        users = users_col.find({})
        count = 0
        lines = []

        async for u in users:
            count += 1
            lines.append(
                f"{count}. {('@'+u['username']) if u.get('username') else 'NoUsername'} | "
                f"ID: {u['user_id']} | "
                f"Premium: {'YES' if u.get('is_premium') else 'NO'} | "
                f"Banned: {'YES' if u.get('banned') else 'NO'}"
            )

            if count >= 50:  # safety limit
                break

        text = "👥 **USERS LIST (Top 50)**\n\n" + "\n".join(lines)
        await message.reply_text(text)

        await send_log(
            client,
            hacker_block(
                "USER DIRECTORY ACCESSED",
                f"👑 Admin ID: {message.from_user.id}\n"
                f"📊 Returned: {count} users"
            )
        )

    # ─── /premiumusers ────────────────────────────────────────────────
    @app.on_message(filters.command("premiumusers") & filters.private)
    async def premium_users_handler(client, message):
        if not is_admin(message.from_user.id):
            return

        users = users_col.find({"is_premium": True})
        count = 0
        lines = []

        async for u in users:
            count += 1
            lines.append(
                f"{count}. {('@'+u['username']) if u.get('username') else 'NoUsername'} | "
                f"ID: {u['user_id']} | "
                f"Expiry: {u.get('premium_expiry','N/A')}"
            )

            if count >= 50:
                break

        if count == 0:
            return await message.reply_text("💎 No premium users found.")

        text = "💎 **PREMIUM USERS (Top 50)**\n\n" + "\n".join(lines)
        await message.reply_text(text)

        await send_log(
            client,
            hacker_block(
                "PREMIUM DIRECTORY ACCESSED",
                f"👑 Admin ID: {message.from_user.id}\n"
                f"💎 Premium Users: {count}"
            )
      )

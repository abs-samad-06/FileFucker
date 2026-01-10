# bot/handlers/profile.py

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime

from bot.services.premium import is_premium
from bot.services.users import get_user


def _fmt_date(dt):
    if not dt:
        return "N/A"
    if isinstance(dt, datetime):
        return dt.strftime("%d-%m-%Y")
    return str(dt)


def register_profile_handler(app, users_col):

    @app.on_message(filters.command("profile") & filters.private)
    async def profile_cmd(client, message: Message):
        user = message.from_user
        user_db = await get_user(users_col, user.id)

        if not user_db:
            await message.reply_text(
                "❌ Profile data not found.\n"
                "Please /start again."
            )
            return

        premium = is_premium(user_db)

        await message.reply_text(
            f"""👤 **Your Profile**

🆔 ID: `{user.id}`
👤 Username: @{user.username or 'N/A'}

💎 Premium: `{'YES' if premium else 'NO'}`
⏳ Expiry: `{_fmt_date(user_db.get('premium_expiry'))}`

📥 Total Downloads: `{user_db.get('total_downloads', 0)}`
🗓 Joined: `{_fmt_date(user_db.get('joined_at'))}`
""",
            disable_web_page_preview=True
      )

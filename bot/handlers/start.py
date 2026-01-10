# bot/handlers/start.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.services.users import get_or_create_user


def register_start_handler(app, users_col):

    @app.on_message(filters.command("start") & filters.private)
    async def start_cmd(client, message):
        user = message.from_user

        await get_or_create_user(users_col, user)

        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📂 Upload File", callback_data="upload")],
                [InlineKeyboardButton("💎 Premium", callback_data="premium")],
                [InlineKeyboardButton("📊 Profile", callback_data="profile")],
            ]
        )

        await message.reply_text(
            text=(
                "🔥 **Welcome to FileFucker Bot**\n\n"
                "📦 Upload your file\n"
                "🔗 Generate secure download links\n"
                "💎 Premium users get direct access\n\n"
                "Start by sending me a file 😈"
            ),
            reply_markup=buttons
        )

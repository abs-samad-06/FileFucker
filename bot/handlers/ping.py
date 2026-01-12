# bot/handlers/ping.py

from pyrogram import filters
from pyrogram.types import Message


def register_ping_handler(app):

    @app.on_message(filters.command("ping") & filters.private)
    async def ping_handler(client, message: Message):
        await message.reply_text(
            "🏓 **PONG!**\n\n"
            "Bot zinda hai MC 😈\n"
            "Tera Heroku bhi chal raha hai.\n\n"
            "Ab file bhej 😎"
        )

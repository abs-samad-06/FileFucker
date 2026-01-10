# bot/handlers/language.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.services.users import get_user


def register_language_handler(app, users_col):

    @app.on_message(filters.command("language") & filters.private)
    async def language_cmd(client, message):
        await message.reply_text(
            "🌐 **Choose Language**",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("English 🇬🇧", callback_data="lang|en"),
                    InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang|hi")
                ]
            ])
        )

    @app.on_callback_query(filters.regex(r"^lang\|"))
    async def language_cb(client, callback):
        _, lang = callback.data.split("|")
        user_id = callback.from_user.id

        await users_col.update_one(
            {"user_id": user_id},
            {"$set": {"language": lang}},
            upsert=True
        )

        if lang == "hi":
            text = "✅ भाषा हिंदी में सेट कर दी गई है"
        else:
            text = "✅ Language set to English"

        await callback.answer(text, show_alert=True)
        await callback.message.edit_text(text)

# bot/handlers/payments.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config


def register_payment_handlers(app, users_col):

    @app.on_message(filters.command("plans") & filters.private)
    async def plans(client, message):
        await message.reply_text(
            "💎 **Premium Plans**\n\n"
            "🗓 7 Days — ₹25\n"
            "🗓 1 Month — ₹70\n"
            "🗓 1 Year — ₹190\n\n"
            "Premium = direct files, no wait 😎",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💸 Buy Premium", callback_data="buy_premium")
            ]])
        )

    @app.on_callback_query(filters.regex("^buy_premium$"))
    async def buy_cb(client, cb):
        await cb.message.edit_text(
            "💸 **Manual Payment**\n\n"
            f"UPI ID: `{Config.UPI_ID}`\n\n"
            "1️⃣ Payment karo\n"
            "2️⃣ Screenshot lo\n"
            "3️⃣ `/request` bhejo with screenshot\n\n"
            "Admin approve karega 💎"
        )

    @app.on_message(filters.command("request") & filters.private)
    async def request_premium(client, message):
        await message.reply_text(
            "📩 **Request Sent**\n\n"
            "Payment screenshot admin ko bhej diya.\n"
            "Verification ke baad premium activate hoga 😎"
  )

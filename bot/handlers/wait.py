# bot/handlers/wait.py

import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.services.shortener import (
    get_link,
    increment_click,
    increment_step,
    deactivate_link
)
from bot.services.logs import send_log, log_link_step


def register_wait_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_callback_query(filters.regex(r"^wait\|"))
    async def wait_flow(client, callback):
        """
        callback_data format:
        wait|<step>|<token>
        """
        try:
            _, step_str, token = callback.data.split("|")
            step = int(step_str)
        except Exception:
            await callback.answer("Invalid request", show_alert=True)
            return

        user = callback.from_user

        # ─── FETCH LINK ───────────────────────────────────────────────
        link = await get_link(db, token)
        if not link:
            await callback.answer("Link expired ya invalid", show_alert=True)
            return

        # ─── SECURITY: SAME USER ONLY ─────────────────────────────────
        if link["owner_id"] != user.id:
            await callback.answer("Access denied", show_alert=True)
            return

        # ─── FETCH FILE ───────────────────────────────────────────────
        file = await files_col.find_one({"file_id": link["file_id"]})
        if not file:
            await deactivate_link(db, token)
            await callback.message.edit_text(
                "❌ File missing.\nLink disabled."
            )
            return

        # ─── STEP 1 ───────────────────────────────────────────────────
        if step == 1:
            await increment_click(db, token)
            await increment_step(db, token, 1)

            await send_log(
                app,
                log_link_step(
                    user.username,
                    user.id,
                    False,
                    token,
                    link.get("file_name", ""),
                    "WAIT_STEP_1"
                )
            )

            await callback.answer("Wait 10 seconds ⏳")
            await asyncio.sleep(10)

            await callback.message.edit_text(
                "⏳ **Step 2 / 3**\n\n"
                "Ab 15 seconds wait karo 😏",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "Continue",
                        callback_data=f"wait|2|{token}"
                    )
                ]])
            )
            return

        # ─── STEP 2 ───────────────────────────────────────────────────
        if step == 2:
            await increment_step(db, token, 2)

            await send_log(
                app,
                log_link_step(
                    user.username,
                    user.id,
                    False,
                    token,
                    link.get("file_name", ""),
                    "WAIT_STEP_2"
                )
            )

            await callback.answer("Wait 15 seconds ⏳")
            await asyncio.sleep(15)

            await callback.message.edit_text(
                "⏳ **Step 3 / 3**\n\n"
                "Last step – 5 seconds bas 😈",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "Continue",
                        callback_data=f"wait|3|{token}"
                    )
                ]])
            )
            return

        # ─── STEP 3 (FINAL DELIVERY) ──────────────────────────────────
        if step == 3:
            await increment_step(db, token, 3)

            await send_log(
                app,
                log_link_step(
                    user.username,
                    user.id,
                    False,
                    token,
                    link.get("file_name", ""),
                    "WAIT_STEP_3_COMPLETE"
                )
            )

            await callback.answer("Almost done ⏳")
            await asyncio.sleep(5)

            # increment file download
            await files_col.update_one(
                {"file_id": link["file_id"]},
                {"$inc": {"downloads": 1}}
            )

            # deactivate link after success (one-time use)
            await deactivate_link(db, token)

            try:
                await app.send_cached_media(
                    chat_id=callback.message.chat.id,
                    file_id=link["file_id"],
                    caption=f"📎 {link.get('file_name', '')}"
                )
            except Exception:
                await callback.message.edit_text(
                    "⚠️ File send nahi ho pa rahi.\n"
                    "Baad me try kar MC."
                )
            return

        # ─── INVALID STEP ─────────────────────────────────────────────
        await callback.answer("Invalid step", show_alert=True)

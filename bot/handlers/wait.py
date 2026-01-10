# bot/handlers/wait.py

import asyncio
from pyrogram import filters
from bot.services.logs import send_log, access_log
from bot.services.premium import is_premium


def register_wait_handler(app, db, users_col):
    files_col = db["files"]

    @app.on_callback_query(filters.regex("^wait_"))
    async def wait_flow(client, callback):
        _, step, file_uid = callback.data.split("|")
        step = int(step)

        file = await files_col.find_one({"file_uid": file_uid})
        user = await users_col.find_one({"user_id": callback.from_user.id})

        if not file:
            await callback.answer("Invalid file", show_alert=True)
            return

        if step == 1:
            await callback.answer("Wait 10 sec ⏳")
            await asyncio.sleep(10)
            await callback.message.edit_text(
                "⏳ Step 2 / 3\nWait 15 sec",
                reply_markup={
                    "inline_keyboard": [[
                        {"text": "Continue", "callback_data": f"wait|2|{file_uid}"}
                    ]]
                }
            )

        elif step == 2:
            await callback.answer("Wait 15 sec ⏳")
            await asyncio.sleep(15)
            await callback.message.edit_text(
                "⏳ Step 3 / 3\nWait 5 sec",
                reply_markup={
                    "inline_keyboard": [[
                        {"text": "Continue", "callback_data": f"wait|3|{file_uid}"}
                    ]]
                }
            )

        elif step == 3:
            await callback.answer("Almost done ⏳")
            await asyncio.sleep(5)

            await files_col.update_one(
                {"file_uid": file_uid},
                {"$inc": {"downloads": 1}}
            )

            await send_log(
                app,
                access_log(callback.from_user, file, False)
            )

            await app.send_cached_media(
                chat_id=callback.message.chat.id,
                file_id=file["file_id"],
                caption=f"📎 {file.get('file_name')}"
      )

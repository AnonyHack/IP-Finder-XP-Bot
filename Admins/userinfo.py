# Admins/userinfo.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import config

def register_userinfo_command(app: Client, db, ADMIN_IDS):
    users_collection = db[config.con.USERS_COLLECTION]
    premium_db = db["premium_users"]
    search_logs = db["search_logs"]

    @app.on_message(filters.command("userinf") & filters.user(ADMIN_IDS))
    async def user_info(client: Client, message):
        try:
            args = message.text.split()
            if len(args) != 2:
                error_text = (
                    "<b>❌ Usage Guide</b>\n\n"
                    "<blockquote>"
                    "<b>Command:</b> /userinf [user_id]\n\n"
                    "<b>Example:</b>\n"
                    "/userinf 123456789"
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_userinfo")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                return

            user_id = int(args[1])
            
            # Get user info from Telegram
            try:
                user = await client.get_users(user_id)
                user_name = user.first_name
                username = f"@{user.username}" if user.username else "Nᴏɴᴇ"
            except:
                user_name = "Uɴᴋɴᴏᴡɴ"
                username = "Nᴏɴᴇ"

            # Get user join date from our database
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data and "join_date" in user_data:
                joined_date = user_data["join_date"].strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                # If no join date in DB, use current time (for new users)
                joined_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                # Save join date if not exists
                users_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"join_date": datetime.utcnow()}},
                    upsert=True
                )

            # Get search count
            search_count = search_logs.count_documents({"user_id": user_id})

            # Get premium info
            premium_info = premium_db.find_one({"user_id": user_id})
            if premium_info:
                plan = "Pʀᴇᴍɪᴜᴍ"
                end_date = premium_info["end_date"]
                time_left = end_date - datetime.utcnow()
                
                if time_left.total_seconds() > 0:
                    days_left = time_left.days
                    hours_left = time_left.seconds // 3600
                    time_left_str = f"{days_left}ᴅ {hours_left}ʜ"
                    expires_str = end_date.strftime("%Y-%m-%d %H:%M:%S UTC")
                    status = "Aᴄᴛɪᴠᴇ ✅"
                else:
                    time_left_str = "Exᴘɪʀᴇᴅ"
                    expires_str = "Exᴘɪʀᴇᴅ"
                    status = "Exᴘɪʀᴇᴅ ❌"
                
                premium_type = "Gɪꜰᴛᴇᴅ" if premium_info.get("is_gifted", False) else "Aᴅᴍɪɴ"
            else:
                plan = "Fʀᴇᴇ"
                time_left_str = "N/ᴀ"
                expires_str = "N/ᴀ"
                premium_type = "N/ᴀ"
                status = "Aᴄᴛɪᴠᴇ ✅"

            # Format the user info message with quoted style
            user_info_text = (
                "<b>🔍 Uꜱᴇʀ Iɴꜰᴏʀᴍᴀᴛɪᴏɴ</b>\n\n"
                "<blockquote>"
                f"🆔 <b>Iᴅ:</b> <code>{user_id}</code>\n"
                f"👤 <b>Nᴀᴍᴇ:</b> {user_name}\n"
                f"📛 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> {username}\n"
                f"📅 <b>Jᴏɪɴᴇᴅ:</b> {joined_date}\n"
                f"🔍 <b>Sᴇᴀʀᴄʜᴇꜱ:</b> {search_count}\n"
                f"💎 <b>Pʟᴀɴ:</b> {plan}\n"
                f"⏳ <b>Tɪᴍᴇ ʟᴇꜰᴛ:</b> {time_left_str}\n"
                f"⏰ <b>Exᴘɪʀᴇꜱ:</b> {expires_str}\n"
                f"🎁 <b>Tʏᴘᴇ:</b> {premium_type}\n"
                f"🔨 <b>Sᴛᴀᴛᴜꜱ:</b> {status}"
                "</blockquote>"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_userinfo")]
            ])

            await message.reply_text(
                user_info_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:
            error_text = (
                "<b>❌ Eʀʀᴏʀ Fᴇᴛᴄʜɪɴɢ Uꜱᴇʀ Iɴꜰᴏ</b>\n\n"
                f"<blockquote>{str(e)}</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_userinfo")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

    # Close button handler
    @app.on_callback_query(filters.regex("close_userinfo"))
    async def close_userinfo(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Uꜱᴇʀ ɪɴꜰᴏ ᴄʟᴏꜱᴇᴅ")

# XP_TOOLS/account.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import config
import pymongo
from Admins.user_management import is_user_banned
from Admins.maintenance import check_maintenance_mode as is_maintenance_mode, get_maintenance_message
from imagen import send_notification

mongo_client = pymongo.MongoClient(config.con.MONGO_URI)
db = mongo_client[config.con.MONGO_DB]
users_collection = db[config.con.USERS_COLLECTION]
premium_db = db["premium_users"]


# Default scans for free users
DEFAULT_SCANS = getattr(config.con, "SCANS_LIMIT", 5)
PREMIUM_SCANS = getattr(config.con, "PREMIUM_SCANS", 50)

def register_account_handler(app: Client, db, is_user_member=None, ask_user_to_join=None):
    @app.on_message(filters.command("myaccount"))
    async def my_account(client: Client, message: Message):
        user_id = message.from_user.id

                # Send a notification after user starts the bot
        try:
            username = message.from_user.username or "NoUsername"
            await send_notification(client, message.from_user.id, username, "Checked Account Info")
        except Exception as e:
            print(f"Notification failed: {e}")  # Don't break the bot if notification fails


        # Check if maintenance mode is active
        if await is_maintenance_mode():
            maintenance_msg = await get_maintenance_message()
            await message.reply_text(
                f"🚧 **Maintenance Mode Active**\n\n{maintenance_msg}\n\n"
                f"⏰ Please try again later.\n"
                f"📞 Contact: @Am_ItachiUchiha for updates",
                parse_mode="Markdown"
            )
            return

        # Check if user is banned
        if await is_user_banned(db, user_id):
            await message.reply_text("🚫 You have been banned from using this bot.")
            return
        
        # Check if user is member of required channels
        if is_user_member and not await is_user_member(client, user_id):
            await ask_user_to_join(client, message)
            return

        # Fetch username and profile photo - FIXED VERSION
        try:
            user = await client.get_users(user_id)
            username = f"@{user.username}" if user.username else user.first_name
            
            # Get user profile photos - FIXED: Convert async generator to list
            photo = None
            photos_list = []
            async for photo_obj in client.get_chat_photos(user_id, limit=1):
                photos_list.append(photo_obj)
            
            if photos_list:
                # Download and send profile photo
                photo = await client.download_media(photos_list[0].file_id, in_memory=True)
                
        except Exception as e:
            print(f"Error fetching user data: {e}")
            username = "Unknown"
            photo = None

        # Fetch premium plan
        premium = premium_db.find_one({"user_id": user_id})
        scans_left = DEFAULT_SCANS  # default scans

        if premium:
            now = datetime.utcnow()
            if premium["end_date"] > now:
                delta = premium["end_date"] - now
                days_left = delta.days
                plan_text = f"Premium {days_left}d"

                # Reset scans for premium users if they have free scans
                user_record = users_collection.find_one({"user_id": user_id})
                if user_record and user_record.get("scans_left", DEFAULT_SCANS) <= DEFAULT_SCANS:
                    users_collection.update_one(
                        {"user_id": user_id},
                        {"$set": {"scans_left": PREMIUM_SCANS}},
                        upsert=True
                    )
                    scans_left = PREMIUM_SCANS
                else:
                    scans_left = user_record.get("scans_left", PREMIUM_SCANS) if user_record else PREMIUM_SCANS
            else:
                plan_text = "FREE"
                user_record = users_collection.find_one({"user_id": user_id})
                scans_left = user_record.get("scans_left", DEFAULT_SCANS) if user_record else DEFAULT_SCANS
                
                # Reset to free scans if premium expired
                if user_record and user_record.get("scans_left", DEFAULT_SCANS) > DEFAULT_SCANS:
                    users_collection.update_one(
                        {"user_id": user_id},
                        {"$set": {"scans_left": DEFAULT_SCANS}},
                        upsert=True
                    )
                    scans_left = DEFAULT_SCANS
        else:
            plan_text = "FREE"
            user_record = users_collection.find_one({"user_id": user_id})
            scans_left = user_record.get("scals_left", DEFAULT_SCANS) if user_record else DEFAULT_SCANS

        # Current time/date
        now_local = datetime.now()
        current_time = now_local.strftime("%I:%M %p")
        current_date = now_local.strftime("%Y-%m-%d")

        # Compose message in quoted style
        text = (
            "<b>👤 Mʏ Aᴄᴄᴏᴜɴᴛ</b>\n\n"
            "<blockquote>"
            f"🆔 <b>Uꜱᴇʀ Iᴅ:</b> <code>{user_id}</code>\n"
            f"👤 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> {username}\n"
            f"💎 <b>Pʟᴀɴ:</b> {plan_text}\n"
            f"🔍 <b>Sᴄᴀɴꜱ Lᴇꜰᴛ:</b> {scans_left}\n"
            f"⏰ <b>Tɪᴍᴇ:</b> {current_time}\n"
            f"📅 <b>Dᴀᴛᴇ:</b> {current_date}\n"
            "</blockquote>"
        )

        # Buttons
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ ᴘʟᴀɴ", url="https://t.me/Am_itachiuchiha")],
            [InlineKeyboardButton("✨ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ", callback_data="premium_benefits")],
            [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_account")]
        ])

        # Send message with or without profile photo
        if photo:
            await message.reply_photo(
                photo=photo,
                caption=text,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply_text(
                text,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )

    # Handle Premium Benefits button click
    @app.on_callback_query(filters.regex("premium_benefits"))
    async def show_premium_benefits(client, callback_query):
        text = (
            "<b>💎 Pʀᴇᴍɪᴜᴍ Pʟᴀɴ Bᴇɴᴇꜰɪᴛꜱ</b>\n\n"
            "<blockquote>"
            f"• <b>{PREMIUM_SCANS} Dᴀɪʟʏ Sᴄᴀɴꜱ</b> (Instead of {DEFAULT_SCANS})\n"
            "• <b>Fᴀꜱᴛᴇʀ Rᴇꜱᴜʟᴛꜱ</b> - Priority processing\n"
            "• <b>Pʀɪᴏʀɪᴛʏ Sᴜᴘᴘᴏʀᴛ</b> - 24/7 dedicated help\n"
            "• <b>Aᴅᴠᴀɴᴄᴇᴅ Fᴇᴀᴛᴜʀᴇꜱ</b> - Early access to new tools\n"
            "• <b>Nᴏ Aᴅꜱ</b> - Clean, uninterrupted experience\n"
            "</blockquote>\n\n"
            "💰 <b>Cᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ꜰᴏʀ ᴘʀɪᴄɪɴɢ:</b> @Am_ItachiUchiha\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        
        # Buttons for premium benefits page
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ", callback_data="back_to_account")],
            [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_account")]
        ])
        
        await callback_query.answer()
        await callback_query.message.edit_text(
            text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    # Handle Go Back button
    @app.on_callback_query(filters.regex("back_to_account"))
    async def back_to_account(client, callback_query):
        user_id = callback_query.from_user.id
        
        # Fetch user data again for the account page
        try:
            user = await client.get_users(user_id)
            username = f"@{user.username}" if user.username else user.first_name
        except:
            username = "Unknown"

        # Fetch premium plan
        premium = premium_db.find_one({"user_id": user_id})
        scans_left = DEFAULT_SCANS

        if premium:
            now = datetime.utcnow()
            if premium["end_date"] > now:
                delta = premium["end_date"] - now
                days_left = delta.days
                plan_text = f"Premium {days_left}d"
                scans_left = PREMIUM_SCANS
            else:
                plan_text = "FREE"
                scans_left = DEFAULT_SCANS
        else:
            plan_text = "FREE"
            scans_left = DEFAULT_SCANS

        # Current time/date
        now_local = datetime.now()
        current_time = now_local.strftime("%I:%M %p")
        current_date = now_local.strftime("%Y-%m-%d")

        # Compose message
        text = (
            "<b>👤 Mʏ Aᴄᴄᴏᴜɴᴛ</b>\n\n"
            "<blockquote>"
            f"🆔 <b>Uꜱᴇʀ Iᴅ:</b> <code>{user_id}</code>\n"
            f"👤 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> {username}\n"
            f"💎 <b>Pʟᴀɴ:</b> {plan_text}\n"
            f"🔍 <b>Sᴄᴀɴꜱ Lᴇꜰᴛ:</b> {scans_left}\n"
            f"⏰ <b>Tɪᴍᴇ:</b> {current_time}\n"
            f"📅 <b>Dᴀᴛᴇ:</b> {current_date}\n"
            "</blockquote>"
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ ᴘʟᴀɴ", url="https://t.me/Am_itachiuchiha")],
            [InlineKeyboardButton("✨ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ", callback_data="premium_benefits")],
            [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_account")]
        ])

        await callback_query.message.edit_text(
            text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    # Handle Close button
    @app.on_callback_query(filters.regex("close_account"))
    async def close_account(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Account info closed")

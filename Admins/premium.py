from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import re
import asyncio
import config

def register_premium_commands(app: Client, db, ADMIN_IDS):
    premium_db = db["premium_users"]
    payments_db = db["payments"]  # auto-created when first insert
    users_collection = db[config.con.USERS_COLLECTION]
    gift_codes_collection = db["gift_codes"] if "gift_codes" in db.list_collection_names() else db.create_collection("gift_codes")

    # ------------- /addprem -------------
    @app.on_message(filters.command("addprem") & filters.user(ADMIN_IDS))
    async def add_premium(client: Client, message):
        try:
            args = message.text.split()
            if len(args) != 3:
                error_text = (
                    "<b>❌ Usage Guide</b>\n\n"
                    "<blockquote>"
                    "<b>Command:</b> /addprem [user_id] [duration]\n\n"
                    "<b>Examples:</b>\n"
                    "/addprem 123456789 30d\n"
                    "/addprem 123456789 12h\n"
                    "/addprem 123456789 45m"
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                return

            user_id = int(args[1])
            duration_str = args[2].lower()

            # Parse duration
            match = re.match(r"(\d+)([dhm])", duration_str)
            if not match:
                error_text = (
                    "<b>❌ Invalid Duration Format</b>\n\n"
                    "<blockquote>"
                    "Please use one of these formats:\n"
                    "• <b>Days:</b> 30d, 7d, 1d\n"
                    "• <b>Hours:</b> 24h, 12h, 1h\n"
                    "• <b>Minutes:</b> 60m, 30m, 15m"
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                return

            num = int(match.group(1))
            unit = match.group(2)
            start_date = datetime.utcnow()
            if unit == "d":
                end_date = start_date + timedelta(days=num)
            elif unit == "h":
                end_date = start_date + timedelta(hours=num)
            elif unit == "m":
                end_date = start_date + timedelta(minutes=num)

            # Fetch username
            try:
                user = await client.get_users(user_id)
                username = user.first_name
            except:
                username = "Unknown"

            # Update premium DB
            premium_db.update_one(
                {"user_id": user_id},
                {"$set": {
                    "username": username, 
                    "start_date": start_date, 
                    "end_date": end_date,
                    "is_gifted": False,  # Admin-added premium
                    "notified": False    # Reset notification status
                }},
                upsert=True
            )

            # Log payment automatically
            payments_db.insert_one({
                "user_id": user_id,
                "username": username,
                "added_by": message.from_user.id,
                "duration": duration_str,
                "amount": 0,  # placeholder for premium cost
                "timestamp": start_date
            })
            
            # After inserting/updating premium user in DB
            # Reset scans immediately
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"scans_left": getattr(config.con, "PREMIUM_SCANS", 10)}},
                upsert=True
            )

            # Notify admin with quoted style
            admin_success_text = (
                "<b>✅ Pʀᴇᴍɪᴜᴍ Aᴅᴅᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ</b>\n\n"
                "<blockquote>"
                f"👤 <b>Uꜱᴇʀ Nᴀᴍᴇ:</b> {username}\n"
                f"⚡️ <b>Uꜱᴇʀ Iᴅ:</b> <code>{user_id}</code>\n"
                f"⏰ <b>Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇꜱꜱ:</b> {duration_str}\n"
                f"📅 <b>Sᴛᴀʀᴛᴇᴅ:</b> {start_date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"⏳ <b>Eɴᴅꜱ:</b> {end_date.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                "</blockquote>"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
            ])

            await message.reply_text(
                admin_success_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

            # Notify user with quoted style
            try:
                user_success_text = (
                    "<b>🎉 Pʀᴇᴍɪᴜᴍ Aᴅᴅᴇᴅ Tᴏ Yᴏᴜʀ Aᴄᴄᴏᴜɴᴛ!</b>\n\n"
                    "<blockquote>"
                    f"⏰ <b>Dᴜʀᴀᴛɪᴏɴ:</b> {duration_str}\n"
                    f"📅 <b>Jᴏɪɴɪɴɢ Dᴀᴛᴇ:</b> {start_date.strftime('%d-%m-%Y')}\n"
                    f"⏱️ <b>Jᴏɪɴɪɴɢ Tɪᴍᴇ:</b> {start_date.strftime('%I:%M:%S %p')}\n\n"
                    f"⌛️ <b>Exᴘɪʀʏ Dᴀᴛᴇ:</b> {end_date.strftime('%d-%m-%Y')}\n"
                    f"⏱️ <b>Exᴘɪʀʏ Tɪᴍᴇ:</b> {end_date.strftime('%I:%M:%S %p')}\n\n"
                    "✨ <b>Eɴᴊᴏʏ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ!</b>"
                    "</blockquote>"
                )

                user_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                ])

                await client.send_message(
                    chat_id=user_id,
                    text=user_success_text,
                    reply_markup=user_keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass

        except Exception as e:
            error_text = (
                "<b>❌ Eʀʀᴏʀ Aᴅᴅɪɴɢ Pʀᴇᴍɪᴜᴍ</b>\n\n"
                f"<blockquote>{str(e)}</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

    # ------------- /removeprem -------------
    @app.on_message(filters.command("removeprem") & filters.user(ADMIN_IDS))
    async def remove_premium(client: Client, message):
        try:
            args = message.text.split()
            if len(args) != 2:
                error_text = (
                    "<b>❌ Usage Guide</b>\n\n"
                    "<blockquote>"
                    "<b>Command:</b> /removeprem [user_id]\n\n"
                    "<b>Example:</b>\n"
                    "/removeprem 123456789"
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                return

            user_id = int(args[1])
            record = premium_db.find_one({"user_id": user_id})
            if not record:
                error_text = (
                    "<b>❌ Uꜱᴇʀ Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
                    "<blockquote>"
                    "This user is not a premium user or doesn't exist."
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                return

            premium_db.delete_one({"user_id": user_id})
            username = record.get("username", "Unknown")

            admin_success_text = (
                "<b>✅ Pʀᴇᴍɪᴜᴍ Rᴇᴍᴏᴠᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ</b>\n\n"
                "<blockquote>"
                f"👤 <b>Uꜱᴇʀ Nᴀᴍᴇ:</b> {username}\n"
                f"⚡️ <b>Uꜱᴇʀ Iᴅ:</b> <code>{user_id}</code>\n\n"
                "⚠️ <b>Pʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ ʜᴀꜱ ʙᴇᴇɴ ʀᴇᴠᴏᴋᴇᴅ</b>"
                "</blockquote>"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
            ])

            await message.reply_text(
                admin_success_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

            # Notify user with quoted style
            try:
                user_notice_text = (
                    "<b>⚠️ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇꜱꜱ Rᴇᴍᴏᴠᴇᴅ</b>\n\n"
                    "<blockquote>"
                    "Yᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ ʜᴀꜱ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ.\n\n"
                    "▸ <b>Sᴛᴀᴛᴜꜱ:</b> Fʀᴇᴇ ᴜꜱᴇʀ\n"
                    "▸ <b>Sᴄᴀɴꜱ:</b> Rᴇꜱᴇᴛ ᴛᴏ ʙᴀꜱɪᴄ ʟɪᴍɪᴛꜱ\n\n"
                    "Cᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ꜰᴏʀ ᴍᴏʀᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ."
                    "</blockquote>"
                )

                user_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                ])

                await client.send_message(
                    user_id, 
                    user_notice_text,
                    reply_markup=user_keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass

        except Exception as e:
            error_text = (
                "<b>❌ Eʀʀᴏʀ Rᴇᴍᴏᴠɪɴɢ Pʀᴇᴍɪᴜᴍ</b>\n\n"
                f"<blockquote>{str(e)}</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

    # ------------- ENHANCED PREMIUM EXPIRY CHECKER -------------
    async def check_expired_premiums():
        while True:
            try:
                now = datetime.utcnow()
                
                # Check for premium that expired in the last 24 hours but haven't been notified
                recently_expired = premium_db.find({
                    "end_date": {
                        "$lte": now,
                        "$gte": now - timedelta(hours=24)
                    },
                    "notified": {"$ne": True}
                })
                
                for user in recently_expired:
                    user_id = user["user_id"]
                    username = user.get("username", "Unknown")
                    is_gifted = user.get("is_gifted", False)

                    # Notify user with quoted style
                    try:
                        if is_gifted:
                            user_expired_text = (
                                "<b>⏳ Gɪꜰᴛᴇᴅ Pʀᴇᴍɪᴜᴍ Exᴘɪʀᴇᴅ</b>\n\n"
                                "<blockquote>"
                                "Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ!\n\n"
                                "Yᴏᴜ ᴄᴀɴ ꜱᴛɪʟʟ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ ᴡɪᴛʜ ꜰʀᴇᴇ ʟɪᴍɪᴛꜱ,\n"
                                "ᴏʀ ʀᴇᴅᴇᴇᴍ ᴀɴᴏᴛʜᴇʀ ɢɪꜰᴛ ᴄᴏᴅᴇ ᴛᴏ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ ᴀɢᴀɪɴ! 🎁"
                                "</blockquote>"
                            )
                        else:
                            user_expired_text = (
                                "<b>⏳ Pʀᴇᴍɪᴜᴍ Sᴜʙꜱᴄʀɪᴘᴛɪᴏɴ Exᴘɪʀᴇᴅ</b>\n\n"
                                "<blockquote>"
                                "Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ!\n\n"
                                "Cᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ᴛᴏ ʀᴇɴᴇᴡ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ.\n"
                                "Wᴇ ʜᴏᴘᴇ ᴛᴏ ꜱᴇᴇ ʏᴏᴜ ʙᴀᴄᴋ ꜱᴏᴏɴ! 🚀"
                                "</blockquote>"
                            )
                        
                        user_keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                        ])

                        await app.send_message(
                            user_id, 
                            user_expired_text,
                            reply_markup=user_keyboard,
                            parse_mode=enums.ParseMode.HTML
                        )
                    except Exception as e:
                        print(f"Error notifying user {user_id}: {e}")

                    # Notify admins with quoted style
                    for admin_id in ADMIN_IDS:
                        try:
                            admin_expired_text = (
                                "<b>❌ Pʀᴇᴍɪᴜᴍ Exᴘɪʀᴇᴅ</b>\n\n"
                                "<blockquote>"
                                f"👤 <b>Uꜱᴇʀ:</b> {username}\n"
                                f"⚡️ <b>Iᴅ:</b> <code>{user_id}</code>\n"
                                f"🎁 <b>Tʏᴘᴇ:</b> {'Gɪꜰᴛᴇᴅ' if is_gifted else 'Aᴅᴍɪɴ'}\n"
                                f"⏰ <b>Exᴘɪʀᴇᴅ:</b> {now.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                                "</blockquote>"
                            )

                            admin_keyboard = InlineKeyboardMarkup([
                                [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                            ])

                            await app.send_message(
                                admin_id, 
                                admin_expired_text,
                                reply_markup=admin_keyboard,
                                parse_mode=enums.ParseMode.HTML
                            )
                        except:
                            pass

                    # Mark as notified but don't delete yet (keep for records)
                    premium_db.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"notified": True}}
                    )

                # Clean up premium records that expired more than 7 days ago
                old_expired = premium_db.find({
                    "end_date": {"$lte": now - timedelta(days=7)}
                })
                
                for user in old_expired:
                    premium_db.delete_one({"_id": user["_id"]})

            except Exception as e:
                print(f"Error in premium expiry check: {e}")
            
            await asyncio.sleep(3600)  # check every hour

    # ------------- PREMIUM EXPIRY WARNING SYSTEM -------------
    async def check_expiring_soon_premiums():
        while True:
            try:
                now = datetime.utcnow()
                
                # Check for premium expiring in next 24 hours but haven't been warned
                expiring_soon = premium_db.find({
                    "end_date": {
                        "$lte": now + timedelta(hours=24),
                        "$gt": now
                    },
                    "warned": {"$ne": True}
                })
                
                for user in expiring_soon:
                    user_id = user["user_id"]
                    username = user.get("username", "Unknown")
                    end_date = user["end_date"]
                    
                    # Calculate time left
                    time_left = end_date - now
                    hours_left = time_left.total_seconds() // 3600
                    
                    # Notify user with quoted style
                    try:
                        user_warning_text = (
                            "<b>⚠️ Pʀᴇᴍɪᴜᴍ Exᴘɪʀᴀᴛɪᴏɴ Wᴀʀɴɪɴɢ</b>\n\n"
                            "<blockquote>"
                            f"Yᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ᴡɪʟʟ ᴇxᴘɪʀᴇ ɪɴ <b>{int(hours_left)} ʜᴏᴜʀꜱ</b>!\n\n"
                            f"⏰ <b>Exᴘɪʀʏ Dᴀᴛᴇ:</b> {end_date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                            "Rᴇɴᴇᴡ ꜱᴏᴏɴ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ᴇɴᴊᴏʏɪɴɢ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ! 🚀"
                            "</blockquote>"
                        )

                        user_keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton("❌ Cʟᴏꜱᴇ", callback_data="close_premium")]
                        ])

                        await app.send_message(
                            user_id,
                            user_warning_text,
                            reply_markup=user_keyboard,
                            parse_mode=enums.ParseMode.HTML
                        )
                    except Exception as e:
                        print(f"Error warning user {user_id}: {e}")
                    
                    # Mark as warned
                    premium_db.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"warned": True}}
                    )

            except Exception as e:
                print(f"Error in premium expiry warning: {e}")
            
            await asyncio.sleep(3600)  # check every hour

    # Close button handler
    @app.on_callback_query(filters.regex("close_premium"))
    async def close_premium(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Pʀᴇᴍɪᴜᴍ ɪɴꜰᴏ ᴄʟᴏꜱᴇᴅ")

    # Start the expiry checkers in background
    app.loop.create_task(check_expired_premiums())
    app.loop.create_task(check_expiring_soon_premiums())

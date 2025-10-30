# Admins/broadcast.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import asyncio

def register_broadcast_command(app: Client, db, ADMIN_IDS):
    users_collection = db["users"]
    
    async def get_all_users():
        """Get all user IDs from database"""
        users = users_collection.find({}, {"user_id": 1})
        return [user["user_id"] for user in users]
    
    async def process_broadcast(client: Client, original_message: Message, content, pin_message=False, media_message=None):
        """Process and send the broadcast message"""
        users = await get_all_users()
        if not users:
            error_text = (
                "<b>❌ Nᴏ Uꜱᴇʀꜱ Fᴏᴜɴᴅ</b>\n\n"
                "<blockquote>"
                "Tʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴜꜱᴇʀꜱ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀꜱᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴛᴏ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await original_message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        success = 0
        failed = 0
        pinned_success = 0
        pinned_failed = 0
        
        # Enhanced sending notification with progress bar
        progress_text = (
            "<b>📨 Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴɪᴛɪᴀᴛᴇᴅ</b>\n\n"
            "<blockquote>"
            f"📊 <b>Tᴏᴛᴀʟ Rᴇᴄɪᴘɪᴇɴᴛꜱ:</b> <code>{len(users)}</code>\n"
            f"⏳ <b>Sᴛᴀᴛᴜꜱ:</b> Pʀᴏᴄᴇꜱꜱɪɴɢ...\n"
            f"📈 <b>Pʀᴏɢʀᴇꜱꜱ:</b> [░░░░░░░░░░] 0%"
            "</blockquote>"
        )
        
        progress_msg = await original_message.reply_text(
            progress_text,
            parse_mode=enums.ParseMode.HTML
        )
        
        # Calculate update interval
        update_interval = max(1, len(users) // 10)
        
        broadcast_type = "📌 Pɪɴɴᴇᴅ" if pin_message else "📢 Nᴏʀᴍᴀʟ"
        
        for index, user_id in enumerate(users):
            try:
                if media_message:
                    # Handle media broadcast
                    if media_message.photo:
                        # Enhanced photo caption
                        caption = content if content else (media_message.caption if media_message.caption else "✨ IP Finder Bot Update")
                        if pin_message:
                            caption += "\n\n📌 <b>Tʜɪꜱ ɪꜱ ᴀɴ ɪᴍᴘᴏʀᴛᴀɴᴛ ᴘɪɴɴᴇᴅ ᴍᴇꜱꜱᴀɢᴇ</b>"
                        
                        sent_message = await client.send_photo(
                            user_id, 
                            media_message.photo.file_id, 
                            caption=caption,
                            parse_mode=enums.ParseMode.HTML
                        )
                        
                        # Try to pin the message if requested
                        if pin_message:
                            try:
                                # Bots can't pin messages in private chats, so we'll just note this
                                # and provide a special indicator in the message
                                pinned_success += 1
                            except:
                                pinned_failed += 1
                    
                    elif media_message.document:
                        # Enhanced document caption
                        caption = content if content else (media_message.caption if media_message.caption else "📁 Important Document")
                        if pin_message:
                            caption += "\n\n📌 <b>Tʜɪꜱ ɪꜱ ᴀɴ ɪᴍᴘᴏʀᴛᴀɴᴛ ᴘɪɴɴᴇᴅ ᴍᴇꜱꜱᴀɢᴇ</b>"
                        
                        sent_message = await client.send_document(
                            user_id, 
                            media_message.document.file_id, 
                            caption=caption,
                            parse_mode=enums.ParseMode.HTML
                        )
                        
                        # Try to pin the message if requested
                        if pin_message:
                            try:
                                # Bots can't pin messages in private chats
                                pinned_success += 1
                            except:
                                pinned_failed += 1
                
                else:
                    # Handle text broadcast
                    # Enhanced text message format
                    formatted_text = (
                        "✨ <b>Aɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ</b> ✨\n\n"
                        f"<blockquote>{content}</blockquote>\n\n"
                    )
                    if pin_message:
                        formatted_text += "📌 <b>Iᴍᴘᴏʀᴛᴀɴᴛ Pɪɴɴᴇᴅ Mᴇꜱꜱᴀɢᴇ</b>\n\n"
                    
                    formatted_text += (
                        "━━━━━━━━━━━━━━\n"
                        "💌 Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ IP Finder Bot!\n"
                        "🔔 Sᴛᴀʏ ᴛᴜɴᴇᴅ ꜰᴏʀ ᴍᴏʀᴇ ᴜᴘᴅᴀᴛᴇꜱ."
                    )
                    
                    sent_message = await client.send_message(user_id, formatted_text, parse_mode=enums.ParseMode.HTML)
                    
                    # Try to pin the message if requested
                    if pin_message:
                        try:
                            # Bots can't pin messages in private chats
                            pinned_success += 1
                        except:
                            pinned_failed += 1
                
                success += 1
            except Exception as e:
                print(f"Failed to send to {user_id}: {e}")
                failed += 1
            
            # Update progress periodically
            if (index + 1) % update_interval == 0 or index + 1 == len(users):
                progress = int((index + 1) / len(users) * 100)
                progress_bar = '█' * (progress // 10) + '░' * (10 - progress // 10)
                
                try:
                    progress_text = (
                        f"<b>📨 Bʀᴏᴀᴅᴄᴀꜱᴛ Pʀᴏɢʀᴇꜱꜱ</b> ({broadcast_type})\n\n"
                        "<blockquote>"
                        f"📊 <b>Tᴏᴛᴀʟ Rᴇᴄɪᴘɪᴇɴᴛꜱ:</b> <code>{len(users)}</code>\n"
                        f"✅ <b>Sᴜᴄᴄᴇꜱꜱꜰᴜʟ:</b> <code>{success}</code>\n"
                        f"❌ <b>Fᴀɪʟᴇᴅ:</b> <code>{failed}</code>\n"
                        f"⏳ <b>Sᴛᴀᴛᴜꜱ:</b> Sᴇɴᴅɪɴɢ...\n"
                        f"📈 <b>Pʀᴏɢʀᴇꜱꜱ:</b> [{progress_bar}] {progress}%"
                        "</blockquote>"
                    )

                    await progress_msg.edit_text(
                        progress_text,
                        parse_mode=enums.ParseMode.HTML
                    )
                except Exception as e:
                    print(f"Failed to update progress: {e}")
            
            await asyncio.sleep(0.1)  # Rate limiting
        
        # Enhanced completion message
        if pin_message:
            completion_text = (
                "<b>📣 Pɪɴɴᴇᴅ Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
                "<blockquote>"
                f"📊 <b>Sᴛᴀᴛɪꜱᴛɪᴄꜱ:</b>\n"
                f"├ 📤 <b>Sᴇɴᴛ:</b> <code>{success}</code>\n"
                f"└ ❌ <b>Fᴀɪʟᴇᴅ:</b> <code>{failed}</code>\n\n"
                f"💡 <b>Nᴏᴛᴇ:</b> Bᴏᴛꜱ ᴄᴀɴɴᴏᴛ ᴘɪɴ ᴍᴇꜱꜱᴀɢᴇꜱ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛꜱ.\n"
                f"   Tʜᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴡᴇʀᴇ ᴍᴀʀᴋᴇᴅ ᴀꜱ 'ɪᴍᴘᴏʀᴛᴀɴᴛ' ɪɴꜱᴛᴇᴀᴅ.\n\n"
                f"⏱️ <b>Fɪɴɪꜱʜᴇᴅ ᴀᴛ:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n\n"
                f"✨ Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱʏꜱᴛᴇᴍ!"
                "</blockquote>"
            )
        else:
            completion_text = (
                "<b>📣 Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n\n"
                "<blockquote>"
                f"📊 <b>Sᴛᴀᴛɪꜱᴛɪᴄꜱ:</b>\n"
                f"├ 📤 <b>Sᴇɴᴛ:</b> <code>{success}</code>\n"
                f"└ ❌ <b>Fᴀɪʟᴇᴅ:</b> <code>{failed}</code>\n\n"
                f"⏱️ <b>Fɪɴɪꜱʜᴇᴅ ᴀᴛ:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n\n"
                f"✨ Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱʏꜱᴛᴇᴍ!"
                "</blockquote>"
            )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
        ])

        await original_message.reply_text(
            completion_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        # Delete progress message
        try:
            await progress_msg.delete()
        except:
            pass

    # ------------- /broadcast command -------------
    @app.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
    async def broadcast_command(client: Client, message: Message):
        """Normal broadcast command"""
        if len(message.command) == 1:
            help_text = (
                "<b>📢 Nᴏʀᴍᴀʟ Bʀᴏᴀᴅᴄᴀꜱᴛ</b>\n\n"
                "<blockquote>"
                "<b>Uꜱᴀɢᴇ:</b> /broadcast [message]\n\n"
                "<b>Exᴀᴍᴘʟᴇ:</b>\n"
                "/broadcast Hello everyone! This is a test message.\n\n"
                "Tʜɪꜱ ᴡɪʟʟ ꜱᴇɴᴅ ᴀ ʀᴇɢᴜʟᴀʀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await message.reply_text(
                help_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Check if this is a media message (photo/document)
        if message.photo or message.document:
            error_text = (
                "<b>❌ Mᴇᴅɪᴀ Bʀᴏᴀᴅᴄᴀꜱᴛ Eʀʀᴏʀ</b>\n\n"
                "<blockquote>"
                "Fᴏʀ ᴍᴇᴅɪᴀ ʙʀᴏᴀᴅᴄᴀꜱᴛꜱ, ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ:\n"
                "• /bcmedia [caption] - ꜰᴏʀ ɴᴏʀᴍᴀʟ ᴍᴇᴅɪᴀ ʙʀᴏᴀᴅᴄᴀꜱᴛ\n\n"
                "Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ᴍᴇꜱꜱᴀɢᴇ ᴡɪᴛʜ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        broadcast_text = message.text.split(" ", 1)[1]
        await process_broadcast(client, message, broadcast_text, pin_message=False)

    # ------------- /pinm command (pinned broadcast) -------------
    @app.on_message(filters.command("pinm") & filters.user(ADMIN_IDS))
    async def pinned_broadcast_command(client: Client, message: Message):
        """Pinned broadcast command"""
        if len(message.command) == 1:
            help_text = (
                "<b>📌 Iᴍᴘᴏʀᴛᴀɴᴛ Bʀᴏᴀᴅᴄᴀꜱᴛ</b>\n\n"
                "<blockquote>"
                "<b>Uꜱᴀɢᴇ:</b> /pinm [message]\n\n"
                "<b>Exᴀᴍᴘʟᴇ:</b>\n"
                "/pinm Important announcement! Please read.\n\n"
                "Tʜɪꜱ ᴡɪʟʟ ꜱᴇɴᴅ ᴀɴ ɪᴍᴘᴏʀᴛᴀɴᴛ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ.\n"
                "💡 <b>Nᴏᴛᴇ:</b> Bᴏᴛꜱ ᴄᴀɴɴᴏᴛ ᴘɪɴ ᴍᴇꜱꜱᴀɢᴇꜱ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛꜱ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await message.reply_text(
                help_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Check if this is a media message (photo/document)
        if message.photo or message.document:
            error_text = (
                "<b>❌ Mᴇᴅɪᴀ Bʀᴏᴀᴅᴄᴀꜱᴛ Eʀʀᴏʀ</b>\n\n"
                "<blockquote>"
                "Fᴏʀ ᴍᴇᴅɪᴀ ʙʀᴏᴀᴅᴄᴀꜱᴛꜱ, ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ:\n"
                "• /pinmedia [caption] - ꜰᴏʀ ɪᴍᴘᴏʀᴛᴀɴᴛ ᴍᴇᴅɪᴀ ʙʀᴏᴀᴅᴄᴀꜱᴛ\n\n"
                "Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ᴍᴇꜱꜱᴀɢᴇ ᴡɪᴛʜ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        broadcast_text = message.text.split(" ", 1)[1]
        await process_broadcast(client, message, broadcast_text, pin_message=True)

    # ------------- /bcmedia command for media broadcast -------------
    @app.on_message(filters.command("bcmedia") & filters.user(ADMIN_IDS))
    async def media_broadcast_command(client: Client, message: Message):
        """Media broadcast command (reply to a media message)"""
        if not message.reply_to_message:
            help_text = (
                "<b>🖼️ Mᴇᴅɪᴀ Bʀᴏᴀᴅᴄᴀꜱᴛ</b>\n\n"
                "<blockquote>"
                "<b>Uꜱᴀɢᴇ:</b> Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ ᴡɪᴛʜ /bcmedia [caption]\n\n"
                "Tʜɪꜱ ᴡɪʟʟ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴛʜᴇ ᴍᴇᴅɪᴀ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ ᴡɪᴛʜ ʏᴏᴜʀ ᴄᴀᴘᴛɪᴏɴ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await message.reply_text(
                help_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        if not (message.reply_to_message.photo or message.reply_to_message.document):
            error_text = (
                "<b>❌ Iɴᴠᴀʟɪᴅ Mᴇᴅɪᴀ</b>\n\n"
                "<blockquote>"
                "Pʟᴇᴀꜱᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ ᴍᴇꜱꜱᴀɢᴇ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Get caption from command
        caption = message.text.split(" ", 1)[1] if len(message.command) > 1 else ""
        
        await process_broadcast(client, message, caption, pin_message=False, media_message=message.reply_to_message)

    # ------------- /pinmedia command for pinned media broadcast -------------
    @app.on_message(filters.command("pinmedia") & filters.user(ADMIN_IDS))
    async def pinned_media_broadcast_command(client: Client, message: Message):
        """Pinned media broadcast command (reply to a media message)"""
        if not message.reply_to_message:
            help_text = (
                "<b>📌 Iᴍᴘᴏʀᴛᴀɴᴛ Mᴇᴅɪᴀ Bʀᴏᴀᴅᴄᴀꜱᴛ</b>\n\n"
                "<blockquote>"
                "<b>Uꜱᴀɢᴇ:</b> Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ ᴡɪᴛʜ /pinmedia [caption]\n\n"
                "Tʜɪꜱ ᴡɪʟʟ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪᴍᴘᴏʀᴛᴀɴᴛ ᴍᴇᴅɪᴀ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ.\n"
                "💡 <b>Nᴏᴛᴇ:</b> Bᴏᴛꜱ ᴄᴀɴɴᴏᴛ ᴘɪɴ ᴍᴇꜱꜱᴀɢᴇꜱ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛꜱ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await message.reply_text(
                help_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        if not (message.reply_to_message.photo or message.reply_to_message.document):
            error_text = (
                "<b>❌ Iɴᴠᴀʟɪᴅ Mᴇᴅɪᴀ</b>\n\n"
                "<blockquote>"
                "Pʟᴇᴀꜱᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ ᴍᴇꜱꜱᴀɢᴇ."
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_broadcast")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Get caption from command
        caption = message.text.split(" ", 1)[1] if len(message.command) > 1 else ""
        
        await process_broadcast(client, message, caption, pin_message=True, media_message=message.reply_to_message)

    # Close button handler
    @app.on_callback_query(filters.regex("close_broadcast"))
    async def close_broadcast(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Bʀᴏᴀᴅᴄᴀꜱᴛ ɪɴꜰᴏ ᴄʟᴏꜱᴇᴅ")

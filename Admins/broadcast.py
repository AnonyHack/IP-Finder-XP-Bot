# Admins/broadcast.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message
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
            await original_message.reply_text("❌ No users found to broadcast to")
            return
        
        success = 0
        failed = 0
        pinned_success = 0
        pinned_failed = 0
        
        # Enhanced sending notification with progress bar
        progress_msg = await original_message.reply_text(
            f"""📨 <b>Broadcast Initiated</b>
            
📊 Total Recipients: <code>{len(users)}</code>
⏳ Status: <i>Processing...</i>

[░░░░░░░░░░] 0%""",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Calculate update interval
        update_interval = max(1, len(users) // 10)
        
        broadcast_type = "📌 PINNED" if pin_message else "📢 NORMAL"
        
        for index, user_id in enumerate(users):
            try:
                if media_message:
                    # Handle media broadcast
                    if media_message.photo:
                        # Enhanced photo caption
                        caption = content if content else (media_message.caption if media_message.caption else "✨ IP Finder Bot Update")
                        if pin_message:
                            caption += "\n\n📌 This is an important pinned message"
                        
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
                            caption += "\n\n📌 This is an important pinned message"
                        
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
                    formatted_text = f"""✨ <b>Announcement</b> ✨\n\n{content}\n\n"""
                    if pin_message:
                        formatted_text += "📌 <b>IMPORTANT PINNED MESSAGE</b>\n\n"
                    if not content.endswith(('🌐', '📢', '🔔', '📣', '📩')):
                        formatted_text += "━━━━━━━━━━━━━━\n"
                        formatted_text += "💌 Thank you for using IP Finder Bot!\n"
                        formatted_text += "🔔 Stay tuned for more updates."
                    
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
                    await progress_msg.edit_text(
                        f"""📨 <b>Broadcast Progress</b> ({broadcast_type})
                        
📊 Total Recipients: <code>{len(users)}</code>
✅ Successful: <code>{success}</code>
❌ Failed: <code>{failed}</code>
⏳ Status: <i>Sending...</i>

[{progress_bar}] {progress}%""",
                        parse_mode=enums.ParseMode.HTML
                    )
                except Exception as e:
                    print(f"Failed to update progress: {e}")
            
            await asyncio.sleep(0.1)  # Rate limiting
        
        # Enhanced completion message
        if pin_message:
            completion_text = f"""📣 <b>Pinned Broadcast Completed!</b>
            
📊 <b>Statistics:</b>
├ 📤 <i>Sent:</i> <code>{success}</code>
└ ❌ <i>Failed:</i> <code>{failed}</code>

💡 <b>Note:</b> Bots cannot pin messages in private chats. 
   The messages were marked as "important" instead.

⏱️ <i>Finished at:</i> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>

✨ <i>Thank you for using our broadcast system!</i>"""
        else:
            completion_text = f"""📣 <b>Broadcast Completed Successfully!</b>
            
📊 <b>Statistics:</b>
├ 📤 <i>Sent:</i> <code>{success}</code>
└ ❌ <i>Failed:</i> <code>{failed}</code>

⏱️ <i>Finished at:</i> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>

✨ <i>Thank you for using our broadcast system!</i>"""
        
        await original_message.reply_text(completion_text, parse_mode=enums.ParseMode.HTML)
        
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
            await message.reply_text(
                "📢 <b>Normal Broadcast</b>\n\n"
                "Usage: /broadcast [message]\n\n"
                "Example: /broadcast Hello everyone! This is a test message.\n\n"
                "This will send a regular message to all users.",
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Check if this is a media message (photo/document)
        if message.photo or message.document:
            await message.reply_text(
                "❌ For media broadcasts, please use:\n"
                "• /bcmedia [caption] - for normal media broadcast\n\n"
                "Reply to a media message with this command."
            )
            return
        
        broadcast_text = message.text.split(" ", 1)[1]
        await process_broadcast(client, message, broadcast_text, pin_message=False)

    # ------------- /pinm command (pinned broadcast) -------------
    @app.on_message(filters.command("pinm") & filters.user(ADMIN_IDS))
    async def pinned_broadcast_command(client: Client, message: Message):
        """Pinned broadcast command"""
        if len(message.command) == 1:
            await message.reply_text(
                "📌 <b>Important Broadcast</b>\n\n"
                "Usage: /pinm [message]\n\n"
                "Example: /pinm Important announcement! Please read.\n\n"
                "This will send an important message to all users.\n"
                "💡 <b>Note:</b> Bots cannot pin messages in private chats.",
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Check if this is a media message (photo/document)
        if message.photo or message.document:
            await message.reply_text(
                "❌ For media broadcasts, please use:\n"
                "• /pinmedia [caption] - for important media broadcast\n\n"
                "Reply to a media message with this command."
            )
            return
        
        broadcast_text = message.text.split(" ", 1)[1]
        await process_broadcast(client, message, broadcast_text, pin_message=True)

    # ------------- /bcmedia command for media broadcast -------------
    @app.on_message(filters.command("bcmedia") & filters.user(ADMIN_IDS))
    async def media_broadcast_command(client: Client, message: Message):
        """Media broadcast command (reply to a media message)"""
        if not message.reply_to_message:
            await message.reply_text(
                "🖼️ <b>Media Broadcast</b>\n\n"
                "Usage: Reply to a photo or document with /bcmedia [caption]\n\n"
                "This will broadcast the media to all users with your caption.",
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        if not (message.reply_to_message.photo or message.reply_to_message.document):
            await message.reply_text("❌ Please reply to a photo or document.")
            return
        
        # Get caption from command
        caption = message.text.split(" ", 1)[1] if len(message.command) > 1 else ""
        
        await process_broadcast(client, message, caption, pin_message=False, media_message=message.reply_to_message)

    # ------------- /pinmedia command for pinned media broadcast -------------
    @app.on_message(filters.command("pinmedia") & filters.user(ADMIN_IDS))
    async def pinned_media_broadcast_command(client: Client, message: Message):
        """Pinned media broadcast command (reply to a media message)"""
        if not message.reply_to_message:
            await message.reply_text(
                "📌 <b>Important Media Broadcast</b>\n\n"
                "Usage: Reply to a photo or document with /pinmedia [caption]\n\n"
                "This will broadcast important media to all users.\n"
                "💡 <b>Note:</b> Bots cannot pin messages in private chats.",
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        if not (message.reply_to_message.photo or message.reply_to_message.document):
            await message.reply_text("❌ Please reply to a photo or document.")
            return
        
        # Get caption from command
        caption = message.text.split(" ", 1)[1] if len(message.command) > 1 else ""
        
        await process_broadcast(client, message, caption, pin_message=True, media_message=message.reply_to_message)
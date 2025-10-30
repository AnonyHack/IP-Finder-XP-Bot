from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from datetime import datetime, timedelta
import asyncio
import threading
import time

# Global maintenance state
maintenance_mode = False
maintenance_message = "🚧 Tʜᴇ Bᴏᴛ ɪꜱ Cᴜʀʀᴇɴᴛʟʏ Uɴᴅᴇʀ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ, Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ Lᴀᴛᴇʀ."
maintenance_end_time = None

# Maintenance duration (1 hour in seconds)
MAINTENANCE_AUTO_DISABLE_TIME = 3600

# Conversation states - track which admin is waiting for maintenance message
maintenance_setup_state = {}


def register_maintenance_commands(app: Client, db, ADMIN_IDS):
    users_collection = db["users"]

    async def get_all_users():
        """Get all user IDs from database"""
        users = users_collection.find({}, {"user_id": 1})
        return [user["user_id"] for user in users]

    # ------------- /mainmode command -------------
    @app.on_message(filters.command("mainmode") & filters.user(ADMIN_IDS))
    async def toggle_maintenance(client: Client, message: Message):
        """Toggle maintenance mode"""
        global maintenance_mode, maintenance_message, maintenance_end_time

        if maintenance_mode:
            # Disable maintenance mode
            maintenance_mode = False
            maintenance_end_time = None

            await message.reply_text(
                "✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Dɪꜱᴀʙʟᴇᴅ**\n\n"
                "🔧 **Aʟʟ ʙᴏᴛ ꜱᴇʀᴠɪᴄᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇꜱᴛᴏʀᴇᴅ ᴛᴏ ɴᴏʀᴍᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴ.**\n\n"
                "▸ **Sᴛᴀᴛᴜꜱ**: Oɴʟɪɴᴇ\n"
                "▸ **Uꜱᴇʀꜱ**: Cᴀɴ ᴀᴄᴄᴇꜱꜱ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ\n"
                "▸ **Tɪᴍᴇ**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        else:
            # Check if command has message attached
            if len(message.command) > 1:
                # Message provided with command
                maintenance_msg_text = " ".join(message.command[1:])
                await process_maintenance_message(client, message, maintenance_msg_text)
            else:
                # Enable maintenance mode setup - ask for message
                maintenance_setup_state[message.from_user.id] = True

                # Create inline cancel button
                cancel_markup = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="cancel_maintenance")]
                    ]
                )

                await message.reply_text(
                    "✍️ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Sᴇᴛᴜᴘ**\n\n"
                    "**Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴇɴᴅ ᴛᴏ ᴜꜱᴇʀꜱ:**\n\n"
                    "▸ **Fᴏʀᴍᴀᴛ**: Yᴏᴜ ᴄᴀɴ ᴜꜱᴇ ʙᴏʟᴅ, ɪᴛᴀʟɪᴄ, ᴏʀ Qᴜᴏᴛᴇᴅ ᴛᴇxᴛ\n"
                    "▸ **Dᴜʀᴀᴛɪᴏɴ**: 1 ʜᴏᴜʀ (ᴀᴜᴛᴏ-ᴅɪꜱᴀʙʟᴇꜱ)\n\n"
                    "**❌ Cʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴀɴᴄᴇʟ**",
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=cancel_markup
                )


    # ------------- Cancel Maintenance Callback -------------
    @app.on_callback_query(filters.regex("cancel_maintenance"))
    async def cancel_maintenance_callback(client: Client, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id

        if user_id in maintenance_setup_state:
            del maintenance_setup_state[user_id]

        await callback_query.message.edit_text(
            "❌ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Sᴇᴛᴜᴘ Cᴀɴᴄᴇʟʟᴇᴅ.**\n\n"
            "🟢 **Nᴏ ᴄʜᴀɴɢᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴀᴅᴇ.**",
            parse_mode=enums.ParseMode.MARKDOWN
        )


    async def process_maintenance_message(client: Client, message: Message, maintenance_msg_text: str):
        """Process the maintenance message and show confirmation"""
        global maintenance_message
        
        maintenance_message = maintenance_msg_text
        
        # Calculate hours and minutes for display
        hours = MAINTENANCE_AUTO_DISABLE_TIME // 3600
        minutes = (MAINTENANCE_AUTO_DISABLE_TIME % 3600) // 60
        time_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        users = await get_all_users()
        
        # Create confirmation buttons
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Aᴄᴄᴇᴘᴛ & Sᴇɴᴅ", callback_data="accept_maintenance"),
                InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ", callback_data="cancel_maintenance")
            ]
        ])
        
        await message.reply_text(
            f"🔧 **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴇꜱꜱᴀɢᴇ Cᴏɴꜰɪʀᴍᴀᴛɪᴏɴ**\n\n"
            f"**Yᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ:**\n"
            f"`{maintenance_message}`\n\n"
            f"**Tʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ ᴀɴᴅ ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ɢᴏ ɪɴᴛᴏ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ.**\n\n"
            f"▸ **Tᴏᴛᴀʟ Uꜱᴇʀꜱ**: `{len(users)}`\n"
            f"▸ **Aᴜᴛᴏ-ᴅɪꜱᴀʙʟᴇ**: `{time_display}`\n\n"
            f"**Cʟɪᴄᴋ 'Aᴄᴄᴇᴘᴛ & Sᴇɴᴅ' ᴛᴏ ᴄᴏɴꜰɪʀᴍ ᴏʀ 'Cᴀɴᴄᴇʟ' ᴛᴏ ᴀʙᴏʀᴛ:**",
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=markup
        )

    # Handler for maintenance message input
    @app.on_message(
        filters.user(ADMIN_IDS)
        & filters.private
        & filters.text
        & ~filters.command(["mainmode", "mainstatus", "start", "help"])
    )
    async def handle_maintenance_input(client: Client, message: Message):
        """Handle maintenance message input"""
        user_id = message.from_user.id

        # Check if user is in maintenance setup state
        if user_id not in maintenance_setup_state:
            return  # Not in setup mode, ignore

        # Check if it's the cancel button
        if message.text.strip() == "❌ Cᴀɴᴄᴇʟ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ":
            # Remove from setup state
            if user_id in maintenance_setup_state:
                del maintenance_setup_state[user_id]
            
            await message.reply_text(
                "❌ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ꜱᴇᴛᴜᴘ ᴄᴀɴᴄᴇʟʟᴇᴅ.**",
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=None
            )
            return

        # Remove from setup state
        del maintenance_setup_state[user_id]

        await process_maintenance_message(client, message, message.text)

    # Callback handler for maintenance confirmation
    @app.on_callback_query(filters.regex(r"^(accept_maintenance|cancel_maintenance)$"))
    async def handle_maintenance_confirmation(client: Client, callback_query):
        global maintenance_mode, maintenance_message, maintenance_end_time
        
        if callback_query.data == "cancel_maintenance":
            await callback_query.answer("❌ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴄᴀɴᴄᴇʟʟᴇᴅ")
            await callback_query.message.edit_text(
                "🛑 **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Cᴀɴᴄᴇʟʟᴇᴅ**\n\n"
                "**Tʜᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ʜᴀꜱ ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ. Tʜᴇ ʙᴏᴛ ʀᴇᴍᴀɪɴꜱ ᴀᴄᴛɪᴠᴇ.**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        if callback_query.data == "accept_maintenance":
            await callback_query.answer("⏳ Eɴᴀʙʟɪɴɢ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ...")
            
            # Enable maintenance mode
            maintenance_mode = True
            maintenance_end_time = datetime.now() + timedelta(seconds=MAINTENANCE_AUTO_DISABLE_TIME)
            
            # Update the confirmation message
            await callback_query.message.edit_text(
                "⏳ **Eɴᴀʙʟɪɴɢ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ...**\n\n"
                "🔄 **Sᴇɴᴅɪɴɢ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ...**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            
            # Send to all users
            users = await get_all_users()
            sent = 0
            failed = 0

            progress_msg = await callback_query.message.reply_text(
                f"📨 **Sᴇɴᴅɪɴɢ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Nᴏᴛɪᴄᴇꜱ**\n\n"
                f"▸ **Tᴏᴛᴀʟ Uꜱᴇʀꜱ**: `{len(users)}`\n"
                f"▸ **Sᴛᴀᴛᴜꜱ**: Pʀᴏᴄᴇꜱꜱɪɴɢ...\n\n"
                f"[░░░░░░░░░░] 0%",
                parse_mode=enums.ParseMode.MARKDOWN,
            )

            # Calculate update interval
            update_interval = max(1, len(users) // 10)

            for index, user_id in enumerate(users):
                try:
                    await client.send_message(
                        user_id,
                        f"⚠️ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Nᴏᴛɪᴄᴇ**\n\n{maintenance_message}\n\n"
                        f"▸ **Eꜱᴛɪᴍᴀᴛᴇᴅ Dᴏᴡɴᴛɪᴍᴇ**: 1 ʜᴏᴜʀ\n"
                        f"▸ **Sᴛᴀᴛᴜꜱ**: Tᴇᴍᴘᴏʀᴀʀʏ ꜱᴇʀᴠɪᴄᴇ ɪɴᴛᴇʀʀᴜᴘᴛɪᴏɴ\n"
                        f"▸ **Cᴏɴᴛᴀᴄᴛ**: @Am_ItachiUchiha ꜰᴏʀ ᴜᴘᴅᴀᴛᴇꜱ",
                        parse_mode=enums.ParseMode.MARKDOWN,
                    )
                    sent += 1
                except Exception as e:
                    print(f"Failed to send to user {user_id}: {e}")
                    failed += 1

                # Update progress periodically
                if (index + 1) % update_interval == 0 or index + 1 == len(users):
                    progress = int((index + 1) / len(users) * 100)
                    progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)

                    try:
                        await progress_msg.edit_text(
                            f"📨 **Sᴇɴᴅɪɴɢ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Nᴏᴛɪᴄᴇꜱ**\n\n"
                            f"▸ **Tᴏᴛᴀʟ Uꜱᴇʀꜱ**: `{len(users)}`\n"
                            f"▸ **Sᴜᴄᴄᴇꜱꜱꜰᴜʟ**: `{sent}`\n"
                            f"▸ **Fᴀɪʟᴇᴅ**: `{failed}`\n"
                            f"▸ **Sᴛᴀᴛᴜꜱ**: Sᴇɴᴅɪɴɢ...\n\n"
                            f"[{progress_bar}] {progress}%",
                            parse_mode=enums.ParseMode.MARKDOWN,
                        )
                    except Exception as e:
                        print(f"Error updating progress: {e}")

                await asyncio.sleep(0.1)  # Rate limiting

            # Calculate hours and minutes for display
            hours = MAINTENANCE_AUTO_DISABLE_TIME // 3600
            minutes = (MAINTENANCE_AUTO_DISABLE_TIME % 3600) // 60
            time_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

            # Final update with results
            await callback_query.message.edit_text(
                f"✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Eɴᴀʙʟᴇᴅ**\n\n"
                f"📊 **Nᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ Rᴇꜱᴜʟᴛꜱ:**\n"
                f"├ ✅ **Sᴜᴄᴄᴇꜱꜱꜰᴜʟ**: `{sent}`\n"
                f"└ ❌ **Fᴀɪʟᴇᴅ**: `{failed}`\n\n"
                f"⏰ **Aᴜᴛᴏ-ᴅɪꜱᴀʙʟᴇ ɪɴ**: `{time_display}`\n"
                f"🕒 **Aᴜᴛᴏ-ᴅɪꜱᴀʙʟᴇ ᴀᴛ**: `{maintenance_end_time.strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
                f"🔧 **Tʜᴇ ʙᴏᴛ ɪꜱ ɴᴏᴡ ɪɴ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ**",
                parse_mode=enums.ParseMode.MARKDOWN
            )

            # Delete progress message
            try:
                await progress_msg.delete()
            except:
                pass

            # Start auto-disable thread
            def auto_disable_maintenance():
                time.sleep(MAINTENANCE_AUTO_DISABLE_TIME)
                
                async def disable_maintenance_async():
                    global maintenance_mode, maintenance_end_time
                    maintenance_mode = False
                    maintenance_end_time = None
                    
                    # Notify all admins
                    for admin_id in ADMIN_IDS:
                        try:
                            await client.send_message(
                                admin_id,
                                "✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Aᴜᴛᴏ-Dɪꜱᴀʙʟᴇᴅ**\n\n"
                                "🔧 **Tʜᴇ ʙᴏᴛ ʜᴀꜱ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴇxɪᴛᴇᴅ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴀɴᴅ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ.**\n\n"
                                "⏰ **Dᴜʀᴀᴛɪᴏɴ**: Cᴏᴍᴘʟᴇᴛᴇᴅ\n"
                                "👥 **Uꜱᴇʀꜱ ɴᴏᴛɪꜰɪᴇᴅ**: Yᴇꜱ",
                                parse_mode=enums.ParseMode.MARKDOWN
                            )
                        except Exception as e:
                            print(f"Failed to notify admin {admin_id}: {e}")
                    
                    # Notify all users
                    users = await get_all_users()
                    for user_id in users:
                        try:
                            await client.send_message(
                                user_id,
                                "🎉 **Bᴏᴛ Iꜱ Bᴀᴄᴋ Oɴʟɪɴᴇ!**\n\n"
                                "✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
                                "🔧 **Tʜᴇ ʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ꜰᴏʀ ᴜꜱᴇ.**\n\n"
                                "✨ **Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʏᴏᴜʀ ᴘᴀᴛɪᴇɴᴄᴇ!**\n\n"
                                "➤ **Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜꜱᴇ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ ɴᴏʀᴍᴀʟʟʏ.**",
                                parse_mode=enums.ParseMode.MARKDOWN
                            )
                            await asyncio.sleep(0.1)  # Rate limiting
                        except:
                            continue

                # Run the async function in a new thread
                def run_async():
                    asyncio.run(disable_maintenance_async())
                
                threading.Thread(target=run_async, daemon=True).start()

            threading.Thread(target=auto_disable_maintenance, daemon=True).start()

    # ------------- /mainstatus command -------------
    @app.on_message(filters.command("mainstatus") & filters.user(ADMIN_IDS))
    async def maintenance_status(client: Client, message: Message):
        """Check maintenance status"""
        global maintenance_mode, maintenance_message, maintenance_end_time

        # Check if maintenance expired
        if maintenance_mode and maintenance_end_time and datetime.now() > maintenance_end_time:
            maintenance_mode = False
            maintenance_end_time = None

        if maintenance_mode:
            time_left = maintenance_end_time - datetime.now()
            hours, remainder = divmod(time_left.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)

            # Create turn off button for active maintenance
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔓 Tᴜʀɴ Oꜰꜰ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="turn_off_maintenance")]
            ])

            status_text = (
                f"🔧 **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Sᴛᴀᴛᴜꜱ**\n\n"
                f"▸ **Sᴛᴀᴛᴜꜱ**: ACTIVE 🚧\n"
                f"▸ **Tɪᴍᴇ Lᴇꜰᴛ**: {int(hours)}ʜ {int(minutes)}ᴍ {int(seconds)}ꜱ\n"
                f"▸ **Aᴜᴛᴏ-ᴅɪꜱᴀʙʟᴇ**: {maintenance_end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"📝 **Mᴇꜱꜱᴀɢᴇ**:\n`{maintenance_message}`"
            )
            
            await message.reply_text(status_text, parse_mode=enums.ParseMode.MARKDOWN, reply_markup=markup)
        else:
            status_text = (
                "✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Sᴛᴀᴛᴜꜱ**\n\n"
                "▸ **Sᴛᴀᴛᴜꜱ**: INACTIVE\n"
                "▸ **Bᴏᴛ**: Fᴜʟʟʏ ᴏᴘᴇʀᴀᴛɪᴏɴᴀʟ\n"
                "▸ **Uꜱᴇʀꜱ**: Cᴀɴ ᴀᴄᴄᴇꜱꜱ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ"
            )

            await message.reply_text(status_text, parse_mode=enums.ParseMode.MARKDOWN)

    # Callback handler for turning off maintenance
    @app.on_callback_query(filters.regex(r"^turn_off_maintenance$"))
    async def handle_turn_off_maintenance(client: Client, callback_query):
        global maintenance_mode, maintenance_end_time
        
        if not maintenance_mode:
            await callback_query.answer("❌ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ")
            await callback_query.message.edit_text(
                "✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Iꜱ Aʟʀᴇᴀᴅʏ Oꜰꜰ**\n\n"
                "**Tʜᴇ ʙᴏᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ɪɴ ɴᴏʀᴍᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴍᴏᴅᴇ.**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        # Disable maintenance mode
        maintenance_mode = False
        maintenance_end_time = None
        
        await callback_query.answer("✅ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴅɪꜱᴀʙʟᴇᴅ")
        
        # Update the status message
        await callback_query.message.edit_text(
            "✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Dɪꜱᴀʙʟᴇᴅ**\n\n"
            "🔧 **Aʟʟ ʙᴏᴛ ꜱᴇʀᴠɪᴄᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇꜱᴛᴏʀᴇᴅ ᴛᴏ ɴᴏʀᴍᴀʟ ᴏᴘᴇʀᴀᴛɪᴏɴ.**\n\n"
            "▸ **Sᴛᴀᴛᴜꜱ**: Oɴʟɪɴᴇ\n"
            "▸ **Uꜱᴇʀꜱ**: Cᴀɴ ᴀᴄᴄᴇꜱꜱ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ\n"
            "▸ **Tɪᴍᴇ**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        # Notify all users that bot is back online
        users = await get_all_users()
        for user_id in users:
            try:
                await client.send_message(
                    user_id,
                    "🎉 **Bᴏᴛ Iꜱ Bᴀᴄᴋ Oɴʟɪɴᴇ!**\n\n"
                    "✅ **Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ**\n\n"
                    "🔧 **Tʜᴇ ʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ꜰᴏʀ ᴜꜱᴇ.**\n\n"
                    "✨ **Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʏᴏᴜʀ ᴘᴀᴛɪᴇɴᴄᴇ!**\n\n"
                    "➤ **Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜꜱᴇ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ ɴᴏʀᴍᴀʟʟʏ.**",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                await asyncio.sleep(0.1)  # Rate limiting
            except:
                continue


# Export the maintenance check function for use in other modules
async def check_maintenance_mode():
    """Check if maintenance mode is active and auto-disable if expired"""
    global maintenance_mode, maintenance_end_time
    if maintenance_mode and maintenance_end_time and datetime.now() > maintenance_end_time:
        maintenance_mode = False
        maintenance_end_time = None
    return maintenance_mode


async def get_maintenance_message():
    """Get the current maintenance message"""
    global maintenance_message
    return maintenance_message



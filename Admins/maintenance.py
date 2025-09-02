# Admins/maintenance.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from datetime import datetime, timedelta
import asyncio
import threading
import time

# Global maintenance state
maintenance_mode = False
maintenance_message = "🚧 The bot is currently under maintenance. Please try again later."
maintenance_end_time = None

def register_maintenance_commands(app: Client, db, ADMIN_IDS):
    users_collection = db["users"]
    
    async def get_all_users():
        """Get all user IDs from database"""
        users = users_collection.find({}, {"user_id": 1})
        return [user["user_id"] for user in users]
    
    async def is_maintenance_mode():
        """Check if maintenance mode is active"""
        global maintenance_mode, maintenance_end_time
        if maintenance_mode and maintenance_end_time and datetime.now() > maintenance_end_time:
            # Auto-disable if time has expired
            maintenance_mode = False
            maintenance_end_time = None
        return maintenance_mode

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
                "✅ **Maintenance Mode Disabled**\n\n"
                "All bot services have been restored to normal operation.\n\n"
                "▸ **Status**: Online\n"
                "▸ **Users**: Can access all features\n"
                "▸ **Time**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            # Enable maintenance mode
            await message.reply_text(
                "🔧 **Maintenance Mode Setup**\n\n"
                "Please enter the maintenance message to send to users:\n\n"
                "▸ **Format**: Text message explaining maintenance\n"
                "▸ **Duration**: 1 hour (auto-disables)\n\n"
                "✘ Type **'cancel'** to abort",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            
            # Store the message object for the next step
            app.maintenance_setup_msg = message

    # Handler for maintenance message input
    @app.on_message(filters.user(ADMIN_IDS) & filters.private & filters.text)
    async def handle_maintenance_message(client: Client, message: Message):

        """Handle maintenance message input"""
        global maintenance_mode, maintenance_message, maintenance_end_time

        # Skip if it's a command (starts with '/')
        if message.text.startswith('/'):
         return
        
        # Check if we're in maintenance setup mode
        if hasattr(app, 'maintenance_setup_msg'):
            if message.text.lower() == "cancel":
                await message.reply_text("❌ Maintenance setup cancelled.")
                delattr(app, 'maintenance_setup_msg')
                return
            
            maintenance_message = message.text
            maintenance_mode = True
            maintenance_end_time = datetime.now() + timedelta(hours=1)
            
            # Send to all users
            users = await get_all_users()
            sent = 0
            failed = 0
            
            progress_msg = await message.reply_text(
                f"📨 **Sending Maintenance Notices**\n\n"
                f"▸ **Total Users**: {len(users)}\n"
                f"▸ **Status**: Processing...\n\n"
                f"[░░░░░░░░░░] 0%",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            
            # Calculate update interval
            update_interval = max(1, len(users) // 10)
            
            for index, user_id in enumerate(users):
                try:
                    await client.send_message(
                        user_id,
                        f"⚠️ **Maintenance Notice**\n\n{maintenance_message}\n\n"
                        f"▸ **Estimated Downtime**: 1 hour\n"
                        f"▸ **Status**: Temporary service interruption\n"
                        f"▸ **Contact**: @Am_ItachiUchiha for updates",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                    sent += 1
                except:
                    failed += 1
                
                # Update progress periodically
                if (index + 1) % update_interval == 0 or index + 1 == len(users):
                    progress = int((index + 1) / len(users) * 100)
                    progress_bar = '█' * (progress // 10) + '░' * (10 - progress // 10)
                    
                    try:
                        await progress_msg.edit_text(
                            f"📨 **Sending Maintenance Notices**\n\n"
                            f"▸ **Total Users**: {len(users)}\n"
                            f"▸ **Successful**: {sent}\n"
                            f"▸ **Failed**: {failed}\n"
                            f"▸ **Status**: Sending...\n\n"
                            f"[{progress_bar}] {progress}%",
                            parse_mode=enums.ParseMode.MARKDOWN
                        )
                    except:
                        pass
                
                await asyncio.sleep(0.1)  # Rate limiting
            
            # Start auto-disable thread
            def auto_disable_maintenance():
                time.sleep(3600)  # 1 hour
                global maintenance_mode, maintenance_end_time
                maintenance_mode = False
                maintenance_end_time = None
            
            threading.Thread(target=auto_disable_maintenance, daemon=True).start()
            
            await message.reply_text(
                f"🔧 **Maintenance Mode Enabled**\n\n"
                f"▸ **Status**: Maintenance active\n"
                f"▸ **Duration**: 1 hour (auto-disables)\n"
                f"▸ **Notifications**: Sent to {sent} users\n"
                f"▸ **Failed**: {failed} users\n\n"
                f"⏰ **Auto-disable at**: {maintenance_end_time.strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            
            # Delete progress message
            try:
                await progress_msg.delete()
            except:
                pass
            
            # Clean up
            delattr(app, 'maintenance_setup_msg')

    # ------------- /mainstatus command -------------
    @app.on_message(filters.command("mainstatus") & filters.user(ADMIN_IDS))
    async def maintenance_status(client: Client, message: Message):
        """Check maintenance status"""
        global maintenance_mode, maintenance_message, maintenance_end_time
        
        if maintenance_mode:
            time_left = maintenance_end_time - datetime.now() if maintenance_end_time else timedelta(0)
            hours, remainder = divmod(time_left.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            await message.reply_text(
                f"🔧 **Maintenance Status**\n\n"
                f"▸ **Status**: ACTIVE 🚧\n"
                f"▸ **Time Left**: {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
                f"▸ **Auto-disable**: {maintenance_end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"📝 **Message**:\n{maintenance_message}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await message.reply_text(
                "✅ **Maintenance Status**\n\n"
                "▸ **Status**: INACTIVE\n"
                "▸ **Bot**: Fully operational\n"
                "▸ **Users**: Can access all features",
                parse_mode=enums.ParseMode.MARKDOWN
            )

# Export the maintenance check function for use in other modules
async def is_maintenance_mode():
    """Check if maintenance mode is active"""
    global maintenance_mode, maintenance_end_time
    if maintenance_mode and maintenance_end_time and datetime.now() > maintenance_end_time:
        # Auto-disable if time has expired
        maintenance_mode = False
        maintenance_end_time = None
    return maintenance_mode

async def get_maintenance_message():
    """Get the current maintenance message"""
    global maintenance_message
    return maintenance_message
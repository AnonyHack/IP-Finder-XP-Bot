# XP_TOOLS/cmds.py
from pyrogram import Client, filters
from pyrogram.types import BotCommand, Message

# Define all bot commands
COMMANDS = [
    BotCommand("start", "🔁 Restart The Bot"),
    BotCommand("account", "🪪 My Profile Page"),
    BotCommand("redeem", "🧧 Redeem Your Gift Code"),
    BotCommand("leaderboard", "📊 Check Top 10 Users"),
    BotCommand("contactus", "👮‍♂️ Contact Us"),
    BotCommand("adminhelp", "🛂 Admin Panel Dashboard"),
    BotCommand("policy", "🛡️ Terms & Policy"),
]

def register_cmds_handler(app: Client):
    """Register the cmds command handler"""
    
    @app.on_message(filters.command("cmds") & filters.private)
    async def update_commands(client: Client, message: Message):
        try:
            await client.set_bot_commands(COMMANDS)
            await message.reply_text("✅ All commands have been updated successfully!")
        except Exception as e:
            await message.reply_text(f"❌ Error updating commands: {e}")
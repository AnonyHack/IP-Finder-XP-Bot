# XP_TOOLS/start.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Admins.user_management import is_user_banned
from Admins.maintenance import is_maintenance_mode, get_maintenance_message

# Expose command metadata
COMMANDS = [("start", "🔁 Restart The Bot")]

def register_start_handler(app: Client, db, users_collection, is_user_member=None, ask_user_to_join=None):
    @app.on_message(filters.command("start") & filters.private)
    async def start_handler(client: Client, message: Message):
        user_id = message.from_user.id

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
            
        inline_keyboard1 = InlineKeyboardMarkup(
            [[InlineKeyboardButton("IP Finder Bot", url="https://t.me/IpTrackerxpbot")]]
        )
        await app.send_photo(
            chat_id=message.chat.id,
            photo="https://te.legra.ph/file/c2e0b27bf45dcaa104633.jpg",
            caption='''
👋 Hello There, 

🤖 I'm IP FINDER BOT⚡️
💫 Send Any Ip Address To Me 
🥳 I'm Also IPV6 Supported 
☘️ Inline Mode
😎 Check IP Risk Level
✅ 24x7 Active
🚀 Deployed On Faster VPS

🧑‍💻How To Use: Start the bot and send any IP address to it. It's so easy✌️

👨‍💻 Developer: @Am_ItachiUchiha ✅
👨‍💻Powered By @Megahubbots
''',
            reply_markup=inline_keyboard1
        )

        # Save user to MongoDB if not exists
        if not users_collection.find_one({"user_id": user_id}):
            users_collection.insert_one({"user_id": user_id})
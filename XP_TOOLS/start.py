from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Admins.user_management import is_user_banned
from Admins.maintenance import check_maintenance_mode as is_maintenance_mode, get_maintenance_message
from config import con  # ✅ import config


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
                f"📞 Contact: {con.BOT_DEVELOPER} for updates",
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

        # Inline buttons (Developer + Powered By + Bot URL)
        inline_keyboard1 = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("👨‍💻 Developer", url=con.BOT_DEVELOPER)],
                [InlineKeyboardButton("👨‍💻 Powered By", url=con.POWERED_BY)],
                [InlineKeyboardButton("🔍 IP Finder Bot", url=con.BOT_URL)]
            ]
        )

        await app.send_photo(
            chat_id=message.chat.id,
            photo=con.START_PHOTO_URL,
            caption='''
👋 Hello There, 

🤖 I'm IP FINDER BOT⚡️
💫 Send Any IP Address To Me 
🥳 I'm Also IPV6 Supported 
☘️ Inline Mode
😎 Check IP Risk Level
✅ 24x7 Active

🧑‍💻How To Use: Start the bot and send any IP address to it. It's so easy✌️
''',
            reply_markup=inline_keyboard1
        )

        # Save user to MongoDB if not exists
        if not users_collection.find_one({"user_id": user_id}):
            users_collection.insert_one({"user_id": user_id})

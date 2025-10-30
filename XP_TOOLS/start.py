from email.mime import message
from xmlrpc import client
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Admins.user_management import is_user_banned
from Admins.maintenance import check_maintenance_mode as is_maintenance_mode, get_maintenance_message
from config import con  # ✅ import config
from imagen import send_notification


def register_start_handler(app: Client, db, users_collection, is_user_member=None, ask_user_to_join=None):
    @app.on_message(filters.command("start") & filters.private)
    async def start_handler(client: Client, message: Message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        # Send a notification after user starts the bot
        try:
            username = message.from_user.username or "NoUsername"
            await send_notification(client, message.from_user.id, username, "Started Bot")
        except Exception as e:
            print(f"Notification failed: {e}")  # Don't break the bot if notification fails

        # Check if maintenance mode is active
        if await is_maintenance_mode():
            maintenance_msg = await get_maintenance_message()
            maintenance_text = (
                "<b>🚧 Maintenance Mode Active</b>\n\n"
                "<blockquote>"
                f"{maintenance_msg}\n\n"
                f"⏰ Please try again later.\n"
                f"📞 Contact: {con.BOT_DEVELOPER} for updates"
                "</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_maintenance")]
            ])
            
            await message.reply_text(
                maintenance_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
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

        # Welcome message with user mention and quoted style
        welcome_text = (
            f"<b>👋 Welcome, {user_name}!</b>\n\n"
            "<blockquote>"
            "🤖 <b>ɪ'ᴍ ɪᴘ ꜰɪɴᴅᴇʀ ʙᴏᴛ ⚡️</b>\n\n"
            "💫 ꜱᴇɴᴅ ᴀɴʏ ɪᴘ ᴀᴅᴅʀᴇꜱꜱ ᴛᴏ ᴍᴇ\n"
            "🥳 ɪ'ᴍ ᴀʟsᴏ ɪᴘv6 sᴜᴘᴘᴏʀᴛᴇᴅ\n"
            "☘️ ɪɴʟɪɴᴇ ᴍᴏᴅᴇ ᴀᴠᴀɪʟᴀʙʟᴇ\n"
            "😎 ᴄʜᴇᴄᴋ ɪᴘ ʀɪsᴋ ʟᴇᴠᴇʟ\n"
            "✅ 24x7 ᴀᴄᴛɪᴠᴇ\n\n"
            "🧑‍💻 <b>ʜᴏᴡ ᴛᴏ ᴜsᴇ:</b> sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴀɴᴅ sᴇɴᴅ ᴀɴʏ ɪᴘ ᴀᴅᴅʀᴇꜱꜱ ᴛᴏ ɪᴛ. ɪᴛ'ꜱ sᴏ ᴇᴀsʏ! ✌️"
            "</blockquote>"
        )

        # Button 1 & 2 side by side, then other buttons below
        inline_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=con.BOT_DEVELOPER),
                InlineKeyboardButton("⚡ ᴄʀᴇᴅɪᴛꜱ", url=con.POWERED_BY)
            ],
            [InlineKeyboardButton("🔍 ɪᴘ ꜰɪɴᴅᴇʀ ʙᴏᴛ", url=con.BOT_URL)],
            [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_start")]
        ])

        await app.send_photo(
            chat_id=message.chat.id,
            photo=con.START_PHOTO_URL,
            caption=welcome_text,
            reply_markup=inline_keyboard,
            parse_mode=enums.ParseMode.HTML
        )

        # Save user to MongoDB if not exists
        if not users_collection.find_one({"user_id": user_id}):
            users_collection.insert_one({"user_id": user_id})

    # Handle close button for start message
    @app.on_callback_query(filters.regex("close_start"))
    async def close_start(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Welcome message closed")

    # Handle close button for maintenance message
    @app.on_callback_query(filters.regex("close_maintenance"))
    async def close_maintenance(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Maintenance info closed")

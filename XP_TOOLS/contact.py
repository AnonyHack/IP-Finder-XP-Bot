# XP_TOOLS/contact.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config
from imagen import send_notification

# Expose command metadata
COMMANDS = [("contactus", " 👮‍♂️ Contact Us")]

def register_contactus_handler(app: Client):
    @app.on_message(filters.command("contactus") & filters.private)
    async def contact_us_command(client: Client, message: Message):
        
        # Get contact admin from config
        contact_admin = getattr(config.con, "BOT_DEVELOPER", "")

                # Send a notification after user starts the bot
        try:
            username = message.from_user.username or "NoUsername"
            await send_notification(client, message.from_user.id, username, "Checked Contact Us")
        except Exception as e:
            print(f"Notification failed: {e}")  # Don't break the bot if notification fails

        
        # Contact message in quoted style
        contact_info_msg = (
            "<b>📞 ★彡( 𝕮𝖔𝖓𝖙𝖆𝖈𝖙 𝖀𝖘 )彡★ 📞</b>\n\n"
            "<blockquote>"
            "📧 <b>Eᴍᴀɪʟ:</b> <code>freenethubbusiness@gmail.com</code>\n\n"
            "Fᴏʀ Aɴʏ Iꜱꜱᴜᴇꜱ, Bᴜꜱɪɴᴇꜱꜱ Dᴇᴀʟꜱ Oʀ IɴQᴜɪʀɪᴇꜱ,\n"
            "Pʟᴇᴀꜱᴇ Rᴇᴀᴄʜ Oᴜᴛ Tᴏ Uꜱ ⬇️\n\n"
            "❗ <i>ONLY FOR BUSINESS AND HELP, DON'T SPAM!</i>"
            "</blockquote>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Mᴇꜱꜱᴀɢᴇ Aᴅᴍɪɴ", url=contact_admin)],
            [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_contact")]
        ])

        await message.reply_text(
            contact_info_msg, 
            reply_markup=keyboard, 
            parse_mode=enums.ParseMode.HTML
        )

    # Handle close button for contact message
    @app.on_callback_query(filters.regex("close_contact"))
    async def close_contact(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Contact info closed")

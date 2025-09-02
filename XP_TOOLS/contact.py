# XP_TOOLS/contact.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

# Expose command metadata
COMMANDS = [("contactus", " 👮‍♂️ Contact Us")]

def register_contactus_handler(app: Client):
    @app.on_message(filters.command("contactus") & filters.private)
    async def contact_us_command(client: Client, message: Message):
        
        contact_info_msg = (
            "📞 ★彡( <b>𝕮𝖔𝖓𝖙𝖆𝖈𝖙 𝖀𝖘</b> )彡★ 📞\n\n"
            "📧 <b>Eᴍᴀɪʟ:</b> <code>freenethubbusiness@gmail.com</code>\n\n"
            "Fᴏʀ Aɴʏ Iꜱꜱᴜᴇꜱ, Bᴜꜱɪɴᴇꜱꜱ Dᴇᴀʟꜱ Oʀ IɴQᴜɪʀɪᴇꜱ,\n"
            "Pʟᴇᴀꜱᴇ Rᴇᴀᴄʜ Oᴜᴛ Tᴏ Uꜱ ⬇️\n\n"
            "❗ <i>ONLY FOR BUSINESS AND HELP, DON'T SPAM!</i>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Mᴇꜱꜱᴀɢᴇ Aᴅᴍɪɴ", url="https://t.me/SILANDO")]
        ])

        await message.reply(contact_info_msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

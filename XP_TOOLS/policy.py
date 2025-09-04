# XP_TOOLS/policy.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.enums import ParseMode
from datetime import datetime

def register_policy_handler(app: Client):
    @app.on_message(filters.command("policy") & filters.private)
    async def policy_command(client: Client, message: Message):
        """Show the bot's usage policy"""
        policy_text = f"""
<blockquote>
📜 <b>Bᴏᴛ Uꜱᴀɢᴇ Pᴏʟɪᴄʏ & Gᴜɪᴅᴇʟɪɴᴇꜱ</b>
━━━━━━━━━━━━━━━━━━━━

🔹 <b>1. Aᴄᴄᴇᴘᴛᴀʙʟᴇ Uꜱᴇ</b>
  ├ ✅ Pᴇʀᴍɪᴛᴛᴇᴅ: Lᴇɢᴀʟ, ɴᴏɴ-ʜᴀʀᴍꜰᴜʟ ᴄᴏɴᴛᴇɴᴛ
  └ ❌ Pʀᴏʜɪʙɪᴛᴇᴅ: Sᴘᴀᴍ, ʜᴀʀᴀꜱꜱᴍᴇɴᴛ, ɪʟʟᴇɢᴀʟ ᴍᴀᴛᴇʀɪᴀʟ

🔹 <b>2. Fᴀɪʀ Uꜱᴀɢᴇ Pᴏʟɪᴄʏ</b>
   ├ ⚖️ Aʙᴜꜱᴇ ᴍᴀʏ ʟᴇᴀᴅ ᴛᴏ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ
   └ 📊 Exᴄᴇꜱꜱɪᴠᴇ ᴜꜱᴀɢᴇ ᴍᴀʏ ʙᴇ ʀᴀᴛᴇ-ʟɪᴍɪᴛᴇᴅ

🔹 <b>3. Fɪɴᴀɴᴄɪᴀʟ Pᴏʟɪᴄʏ</b>
   ├ 💳 Aʟʟ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴꜱ ᴀʀᴇ ꜰɪɴᴀʟ
   └ 🔄 Nᴏ ʀᴇꜰᴜɴᴅꜱ ꜰᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ꜱᴇʀᴠɪᴄᴇꜱ

🔹 <b>4. Pʀɪᴠᴀᴄʏ Cᴏᴍᴍɪᴛᴍᴇɴᴛ</b>
   ├ 🔒 Yᴏᴜʀ ᴅᴀᴛᴀ ꜱᴛᴀʏꜱ ᴄᴏɴꜰɪᴅᴇɴᴛɪᴀʟ
   └ 🤝 Nᴇᴠᴇʀ ꜱʜᴀʀᴇᴅ ᴡɪᴛʜ ᴛʜɪʀᴅ ᴘᴀʀᴛɪᴇꜱ

🔹 <b>5. Pʟᴀᴛꜰᴏʀᴍ Cᴏᴍᴘʟɪᴀɴᴄᴇ</b>
   ├ ✋ Mᴜꜱᴛ ꜰᴏʟʟᴏᴡ Tᴇʟᴇɢʀᴀᴍ'ꜱ TᴏS
   └ 🌐 Aʟʟ ᴄᴏɴᴛᴇɴᴛ ᴍᴜꜱᴛ ʙᴇ ʟᴇɢᴀʟ ɪɴ ʏᴏᴜʀ ᴊᴜʀɪꜱᴅɪᴏɴ

⚠️ <b>CᴏɴꜱᴇQᴜᴇɴᴄᴇꜱ ᴏꜰ Vɪᴏʟᴀᴛɪᴏɴ</b>
   ├ ⚠️ Fɪʀꜱᴛ ᴏꜰꜰᴇɴꜱᴇ: Wᴀʀɴɪɴɢ
   ├ 🔇 Rᴇᴘᴇᴀᴛᴇᴅ ᴠɪᴏʟᴀᴛɪᴏɴꜱ: Tᴇᴍᴘᴏʀᴀʀʏ ꜱᴜꜱᴘᴇɴꜱɪᴏɴ
   └ 🚫 Sᴇᴠᴇʀᴇ ᴄᴀꜱᴇꜱ: Pᴇʀᴍᴀɴᴇɴᴛ ʙᴀɴ

📅 <i>Lᴀꜱᴛ ᴜᴘᴅᴀᴛᴇᴅ:</i> {datetime.now().strftime('%Y-%m-%d')}
━━━━━━━━━━━━━━━━━━━━
💡 Nᴇᴇᴅ ʜᴇʟᴘ? Cᴏɴᴛᴀᴄᴛ @SocialHubBoosterTMbot
</blockquote>
"""

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Accept Policy", callback_data="accept_policy")]
        ])

        await message.reply(policy_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    @app.on_callback_query(filters.regex("^accept_policy$"))
    async def accept_policy_callback(client: Client, callback_query: CallbackQuery):
        await callback_query.answer(
            "🙏 Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʏᴏᴜʀ Cᴏᴏᴘᴇʀᴀᴛɪᴏɴ!",
            show_alert=True
        )

        try:
            # Remove the button
            await callback_query.edit_message_reply_markup(reply_markup=None)

            # Delete the policy message after confirmation
            await callback_query.message.delete()
        except Exception as e:
            print(f"Error deleting policy message: {e}")

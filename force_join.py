# force_join.py
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
import config

async def is_user_member(client, user_id):
    """Check if user is member of all required channels"""
    for ch in config.con.REQUIRED_CHANNELS:
        chat = ch.get("chat") or ch.get("url").split("/")[-1]
        try:
            # Handle both channel IDs and usernames
            if str(chat).startswith('-100'):
                chat_id = int(chat)
            else:
                chat_id = chat.lstrip('@')  # Remove @ if present
                
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in [enums.ChatMemberStatus.MEMBER, 
                                   enums.ChatMemberStatus.ADMINISTRATOR, 
                                   enums.ChatMemberStatus.OWNER]:
                return False
        except UserNotParticipant:
            return False
        except Exception as e:
            print(f"Error checking membership for {chat}: {e}")
            return False
    return True

async def ask_user_to_join(client, message):
    """Ask user to join required channels"""
    buttons = [[InlineKeyboardButton(ch["label"], url=ch["url"])] for ch in config.con.REQUIRED_CHANNELS]
    buttons.append([InlineKeyboardButton("✅ Verify Membership", callback_data="verify_membership")])
    
    await message.reply(
        "🚨 To use this bot, you must join our channels first! 🚨\n"
        "Click the buttons below to join, then press '✅ Verify Membership' to continue.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def register_force_join_handlers(app: Client):
    """Register all force join related handlers"""
    
    @app.on_callback_query(filters.regex("verify_membership"))
    async def refresh_join_status(client, callback_query):
        user_id = callback_query.from_user.id
        if await is_user_member(client, user_id):
            await callback_query.message.delete()
            await client.send_message(
                user_id,
                "✅ Verification successful! You can now use all bot commands."
            )
        else:
            await callback_query.answer("❌ You haven't joined all channels yet!", show_alert=True)
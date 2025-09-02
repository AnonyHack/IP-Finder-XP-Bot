# XP_TOOLS/account.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import config
import pymongo
from Admins.user_management import is_user_banned
from Admins.maintenance import is_maintenance_mode, get_maintenance_message

mongo_client = pymongo.MongoClient(config.con.MONGO_URI)
db = mongo_client[config.con.MONGO_DB]
users_collection = db[config.con.USERS_COLLECTION]
premium_db = db["premium_users"]

# Expose command metadata
COMMANDS = [("myaccount", " 🪪 My Profile Page")]

# Default scans for free users
DEFAULT_SCANS = getattr(config.con, "SCANS_LIMIT", 10)
PREMIUM_SCANS = getattr(config.con, "PREMIUM_SCANS", 50)

def register_account_handler(app: Client, db, is_user_member=None, ask_user_to_join=None):
    @app.on_message(filters.command("myaccount"))
    async def my_account(client: Client, message: Message):
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

        # Fetch username
        try:
            user = await client.get_users(user_id)
            username = f"@{user.username}" if user.username else user.first_name
        except:
            username = "Unknown"

        # Fetch premium plan
        premium = premium_db.find_one({"user_id": user_id})
        scans_left = DEFAULT_SCANS  # default scans

        if premium:
            now = datetime.utcnow()
            if premium["end_date"] > now:
                delta = premium["end_date"] - now
                days_left = delta.days
                plan_text = f"Premium {days_left}d"

                # Reset scans for premium users if they have free scans
                user_record = users_collection.find_one({"user_id": user_id})
                if user_record and user_record.get("scans_left", DEFAULT_SCANS) <= DEFAULT_SCANS:
                    users_collection.update_one(
                        {"user_id": user_id},
                        {"$set": {"scans_left": PREMIUM_SCANS}},
                        upsert=True
                    )
                    scans_left = PREMIUM_SCANS
                else:
                    scans_left = user_record.get("scans_left", PREMIUM_SCANS) if user_record else PREMIUM_SCANS
            else:
                plan_text = "FREE"
                user_record = users_collection.find_one({"user_id": user_id})
                scans_left = user_record.get("scans_left", DEFAULT_SCANS) if user_record else DEFAULT_SCANS
                
                # Reset to free scans if premium expired
                if user_record and user_record.get("scans_left", DEFAULT_SCANS) > DEFAULT_SCANS:
                    users_collection.update_one(
                        {"user_id": user_id},
                        {"$set": {"scans_left": DEFAULT_SCANS}},
                        upsert=True
                    )
                    scans_left = DEFAULT_SCANS
        else:
            plan_text = "FREE"
            user_record = users_collection.find_one({"user_id": user_id})
            scans_left = user_record.get("scans_left", DEFAULT_SCANS) if user_record else DEFAULT_SCANS

        # Current time/date
        now_local = datetime.now()
        current_time = now_local.strftime("%I:%M %p")
        current_date = now_local.strftime("%Y-%m-%d")

        # Compose message
        text = (
            f"𝗠𝘆 𝗔𝗰𝗰𝗼𝘂𝗻𝘁\n\n"
            f"🆔 Uꜱᴇʀ Iᴅ: {user_id}\n"
            f"👤 Uꜱᴇʀɴᴀᴍᴇ: {username}\n"
            f"🗣 Plan: {plan_text}\n"
            f"⏰ Scans Limit: {scans_left} Scans Left\n"
            f"⏰ Tɪᴍᴇ: {current_time}\n"
            f"📅 Dᴀᴛᴇ: {current_date}"
        )

        # Buttons
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Upgrade Plan", url="https://t.me/Am_itachiuchiha")],
            [InlineKeyboardButton("Premium Benefits", callback_data="premium_benefits")]
        ])

        await message.reply_text(text, reply_markup=buttons)

    # Handle Premium Benefits button click
    @app.on_callback_query(filters.regex("premium_benefits"))
    async def show_premium_benefits(client, callback_query):
        text = (
            "💎 Premium Plan Benefits:\n\n"
            f"• {PREMIUM_SCANS} Daily Scans (Instead of {DEFAULT_SCANS})\n"
            "• Faster Results\n"
            "• Priority Support\n"
            "• Additional Features Coming Soon\n\n"
            "💰 Contact admin for pricing"
        )
        await callback_query.answer()
        await callback_query.message.edit_text(text)
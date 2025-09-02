# Admins/userinfo.py
from pyrogram import Client, filters
from datetime import datetime
import config

def register_userinfo_command(app: Client, db, ADMIN_IDS):
    users_collection = db[config.con.USERS_COLLECTION]
    premium_db = db["premium_users"]
    search_logs = db["search_logs"]

    @app.on_message(filters.command("userinf") & filters.user(ADMIN_IDS))
    async def user_info(client: Client, message):
        try:
            args = message.text.split()
            if len(args) != 2:
                await message.reply_text("Usage: /userinf [user_id]")
                return

            user_id = int(args[1])
            
            # Get user info from Telegram
            try:
                user = await client.get_users(user_id)
                user_name = user.first_name
                username = f"@{user.username}" if user.username else "None"
            except:
                user_name = "Unknown"
                username = "None"

            # Get user join date from our database
            user_data = users_collection.find_one({"user_id": user_id})
            if user_data and "join_date" in user_data:
                joined_date = user_data["join_date"].strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                # If no join date in DB, use current time (for new users)
                joined_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                # Save join date if not exists
                users_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"join_date": datetime.utcnow()}},
                    upsert=True
                )

            # Get search count
            search_count = search_logs.count_documents({"user_id": user_id})

            # Get premium info
            premium_info = premium_db.find_one({"user_id": user_id})
            if premium_info:
                plan = "Premium"
                end_date = premium_info["end_date"]
                time_left = end_date - datetime.utcnow()
                
                if time_left.total_seconds() > 0:
                    days_left = time_left.days
                    hours_left = time_left.seconds // 3600
                    time_left_str = f"{days_left}d {hours_left}h"
                    expires_str = end_date.strftime("%Y-%m-%d %H:%M:%S UTC")
                    status = "ACTIVE ✅"
                else:
                    time_left_str = "Expired"
                    expires_str = "Expired"
                    status = "EXPIRED ❌"
                
                premium_type = "Gifted" if premium_info.get("is_gifted", False) else "Admin"
            else:
                plan = "Free"
                time_left_str = "N/A"
                expires_str = "N/A"
                premium_type = "N/A"
                status = "ACTIVE ✅"

            # Format the user info message
            user_info_text = (
                "┌──────────────────────\n"
                f"│ 🔍 𝗨𝘀𝗲𝗿 𝗜𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼𝗻:\n"
                f"│ ━━━━━━━━━━━━━━━━━━━━━━\n"
                f"│ 🆔 Iᴅ: {user_id}\n"
                f"│ 👤 Nᴀᴍᴇ: {user_name}\n"
                f"│ 📛 Uꜱᴇʀɴᴀᴍᴇ: {username}\n"
                f"│ 💰 Joined: {joined_date}\n"
                f"│ 📊 Searches: {search_count}\n"
                f"│ 👥 Plan: {plan}\n"
                f"│ 📅 Time left: {time_left_str}\n"
                f"│ ⏰ Expires: {expires_str}\n"
                f"│ 🎁 Type: {premium_type}\n"
                f"│ 🔨 Sᴛᴀᴛᴜꜱ: {status}\n"
                "└─────────────────────"
            )

            await message.reply_text(user_info_text)

        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")
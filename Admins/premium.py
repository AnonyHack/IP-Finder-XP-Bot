# Admins/premium.py
from pyrogram import Client, filters
from datetime import datetime, timedelta
import re
import asyncio
import config

def register_premium_commands(app: Client, db, ADMIN_IDS):
    premium_db = db["premium_users"]
    payments_db = db["payments"]  # auto-created when first insert
    users_collection = db[config.con.USERS_COLLECTION]
    gift_codes_collection = db["gift_codes"] if "gift_codes" in db.list_collection_names() else db.create_collection("gift_codes")

    # ------------- /addprem -------------
    @app.on_message(filters.command("addprem") & filters.user(ADMIN_IDS))
    async def add_premium(client: Client, message):
        try:
            args = message.text.split()
            if len(args) != 3:
                await message.reply_text(
                    "Usage: /addprem [user_id] [duration]\n"
                    "Examples: 30d, 12h, 45m"
                )
                return

            user_id = int(args[1])
            duration_str = args[2].lower()

            # Parse duration
            match = re.match(r"(\d+)([dhm])", duration_str)
            if not match:
                await message.reply_text("Invalid duration format. Use days(d), hours(h), or minutes(m).")
                return

            num = int(match.group(1))
            unit = match.group(2)
            start_date = datetime.utcnow()
            if unit == "d":
                end_date = start_date + timedelta(days=num)
            elif unit == "h":
                end_date = start_date + timedelta(hours=num)
            elif unit == "m":
                end_date = start_date + timedelta(minutes=num)

            # Fetch username
            try:
                user = await client.get_users(user_id)
                username = user.first_name
            except:
                username = "Unknown"

            # Update premium DB
            premium_db.update_one(
                {"user_id": user_id},
                {"$set": {
                    "username": username, 
                    "start_date": start_date, 
                    "end_date": end_date,
                    "is_gifted": False,  # Admin-added premium
                    "notified": False    # Reset notification status
                }},
                upsert=True
            )

            # Log payment automatically
            payments_db.insert_one({
                "user_id": user_id,
                "username": username,
                "added_by": message.from_user.id,
                "duration": duration_str,
                "amount": 0,  # placeholder for premium cost
                "timestamp": start_date
            })
            
            # After inserting/updating premium user in DB
            # Reset scans immediately
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"scans_left": getattr(config.con, "PREMIUM_SCANS", 10)}},
                upsert=True
            )

            # Notify admin
            await message.reply_text(
                f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴛᴏ ᴛʜᴇ ᴜꜱᴇʀ.\n"
                f"👤 ᴜꜱᴇʀ ɴᴀᴍᴇ : {username}\n"
                f"⚡️ ᴜꜱᴇʀ ɪᴅ : {user_id}\n"
                f"⏰ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱꜱ : {duration_str}"
            )

            # Notify user
            try:
                await client.send_message(
                    chat_id=user_id,
                    text=(
                        f"ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜰᴏʀ {duration_str} ᴇɴᴊᴏʏ 😀\n\n"
                        f"⏳ ᴊᴏɪɴɪɴɢ ᴅᴀᴛᴇ : {start_date.strftime('%d-%m-%Y')}\n"
                        f"⏱️ ᴊᴏɪɴɪɴɢ ᴛɪᴍᴇ : {start_date.strftime('%I:%M:%S %p')}\n\n"
                        f"⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ : {end_date.strftime('%d-%m-%Y')}\n"
                        f"⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ : {end_date.strftime('%I:%M:%S %p')}"
                    )
                )
            except:
                pass

        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")

    # ------------- /removeprem -------------
    @app.on_message(filters.command("removeprem") & filters.user(ADMIN_IDS))
    async def remove_premium(client: Client, message):
        try:
            args = message.text.split()
            if len(args) != 2:
                await message.reply_text("Usage: /removeprem [user_id]")
                return

            user_id = int(args[1])
            record = premium_db.find_one({"user_id": user_id})
            if not record:
                await message.reply_text("❌ This user is not a premium user.")
                return

            premium_db.delete_one({"user_id": user_id})
            username = record.get("username", "Unknown")

            await message.reply_text(
                f"ᴘʀᴇᴍɪᴜᴍ ʀᴇᴍᴏᴠᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.\n"
                f"👤 ᴜꜱᴇʀ ɴᴀᴍᴇ : {username}\n"
                f"⚡️ ᴜꜱᴇʀ ɪᴅ : {user_id}"
            )

            try:
                await client.send_message(user_id, "⚠️ Your premium access has been removed by the admin.")
            except:
                pass

        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")

    # ------------- ENHANCED PREMIUM EXPIRY CHECKER -------------
    async def check_expired_premiums():
        while True:
            try:
                now = datetime.utcnow()
                
                # Check for premium that expired in the last 24 hours but haven't been notified
                recently_expired = premium_db.find({
                    "end_date": {
                        "$lte": now,
                        "$gte": now - timedelta(hours=24)
                    },
                    "notified": {"$ne": True}
                })
                
                for user in recently_expired:
                    user_id = user["user_id"]
                    username = user.get("username", "Unknown")
                    is_gifted = user.get("is_gifted", False)

                    # Notify user
                    try:
                        if is_gifted:
                            message_text = (
                                "⏳ Your gifted premium subscription has ended!\n\n"
                                "Thank you for using our premium features. "
                                "You can still use the bot with free limits, "
                                "or redeem another gift code to get premium again! 🎁"
                            )
                        else:
                            message_text = (
                                "⏳ Your premium subscription has ended!\n\n"
                                "Thank you for using our premium features. "
                                "Contact admin to renew your premium access. 🚀"
                            )
                        
                        await app.send_message(user_id, message_text)
                    except Exception as e:
                        print(f"Error notifying user {user_id}: {e}")

                    # Notify admins
                    for admin_id in ADMIN_IDS:
                        try:
                            await app.send_message(
                                admin_id, 
                                f"❌ Premium expired for {username} ({user_id})\n"
                                f"Type: {'Gifted' if is_gifted else 'Admin'}"
                            )
                        except:
                            pass

                    # Mark as notified but don't delete yet (keep for records)
                    premium_db.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"notified": True}}
                    )

                # Clean up premium records that expired more than 7 days ago
                old_expired = premium_db.find({
                    "end_date": {"$lte": now - timedelta(days=7)}
                })
                
                for user in old_expired:
                    premium_db.delete_one({"_id": user["_id"]})

            except Exception as e:
                print(f"Error in premium expiry check: {e}")
            
            await asyncio.sleep(3600)  # check every hour

    # ------------- PREMIUM EXPIRY WARNING SYSTEM -------------
    async def check_expiring_soon_premiums():
        while True:
            try:
                now = datetime.utcnow()
                
                # Check for premium expiring in next 24 hours but haven't been warned
                expiring_soon = premium_db.find({
                    "end_date": {
                        "$lte": now + timedelta(hours=24),
                        "$gt": now
                    },
                    "warned": {"$ne": True}
                })
                
                for user in expiring_soon:
                    user_id = user["user_id"]
                    username = user.get("username", "Unknown")
                    end_date = user["end_date"]
                    
                    # Calculate time left
                    time_left = end_date - now
                    hours_left = time_left.total_seconds() // 3600
                    
                    # Notify user
                    try:
                        await app.send_message(
                            user_id,
                            f"⚠️ Your premium subscription will expire in {int(hours_left)} hours!\n\n"
                            f"Expiry date: {end_date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                            "Renew soon to continue enjoying premium features! 🚀"
                        )
                    except Exception as e:
                        print(f"Error warning user {user_id}: {e}")
                    
                    # Mark as warned
                    premium_db.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"warned": True}}
                    )

            except Exception as e:
                print(f"Error in premium expiry warning: {e}")
            
            await asyncio.sleep(3600)  # check every hour

    # Start the expiry checkers in background
    app.loop.create_task(check_expired_premiums())
    app.loop.create_task(check_expiring_soon_premiums())
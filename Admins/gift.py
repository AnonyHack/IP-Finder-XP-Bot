# Admins/gift.py
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import random
import string
import config


def generate_gift_code(length=12):
    """Generate a random gift code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def register_gift_commands(app: Client, db, ADMIN_IDS):
    gift_codes_collection = db["gift_codes"]
    premium_collection = db["premium_users"]
    users_collection = db[config.con.USERS_COLLECTION]

    @app.on_message(filters.command("giftc") & filters.user(ADMIN_IDS))
    async def create_gift_code(client: Client, message: Message):
        try:
            # Parse command arguments
            args = message.text.split()
            if len(args) < 3:
                await message.reply_text("❌ Usage: /giftc <duration> <validity>\n\n"
                                       "Example: /giftc 3 1h - Creates a code that gives 3 days premium, valid for 1 hour")
                return

            premium_duration = int(args[1])
            validity_str = args[2].lower()
            
            # Parse validity duration
            if validity_str.endswith('h'):
                validity_hours = int(validity_str[:-1])
                validity = timedelta(hours=validity_hours)
            elif validity_str.endswith('d'):
                validity_days = int(validity_str[:-1])
                validity = timedelta(days=validity_days)
            elif validity_str.endswith('m'):
                validity_minutes = int(validity_str[:-1])
                validity = timedelta(minutes=validity_minutes)
            else:
                await message.reply_text("❌ Invalid validity format. Use h (hours), d (days), or m (minutes)")
                return

            # Generate gift code
            code = generate_gift_code()
            expires_at = datetime.utcnow() + validity
            
            # Save to database
            gift_codes_collection.insert_one({
                "code": code,
                "premium_duration": premium_duration,  # in days
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "created_by": message.from_user.id,
                "used_by": None,
                "used_at": None,
                "is_used": False
            })

            await message.reply_text(
                f"🎁 Gift Code Created!\n\n"
                f"🔑 Code: `{code}`\n"
                f"⭐ Premium Duration: {premium_duration} days\n"
                f"⏰ Valid Until: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                f"Share this code with users to redeem premium features!"
            )

        except Exception as e:
            await message.reply_text(f"❌ Error creating gift code: {str(e)}")

    @app.on_message(filters.command("redeem"))
    async def redeem_gift_code(client: Client, message: Message):
        try:
            args = message.text.split()
            if len(args) < 2:
                await message.reply_text("❌ Usage: /redeem <gift_code>")
                return

            code = args[1].upper()
            
            # Check if code exists and is valid
            gift_code = gift_codes_collection.find_one({"code": code, "is_used": False})
            
            if not gift_code:
                await message.reply_text("❌ Invalid or already used gift code!")
                return
            
            if gift_code["expires_at"] < datetime.utcnow():
                await message.reply_text("❌ This gift code has expired!")
                return

            user_id = message.from_user.id
            
            # Check if user already has premium
            existing_premium = premium_collection.find_one({"user_id": user_id})
            
            if existing_premium:
                # Extend existing premium
                new_end_date = existing_premium["end_date"] + timedelta(days=gift_code["premium_duration"])
                premium_collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"end_date": new_end_date}}
                )
            else:
                # Create new premium entry
                start_date = datetime.utcnow()
                end_date = start_date + timedelta(days=gift_code["premium_duration"])
                premium_collection.insert_one({
                    "user_id": user_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "gift_code": code,
                    "is_gifted": True
                })

            # Mark code as used
            gift_codes_collection.update_one(
                {"code": code},
                {"$set": {
                    "is_used": True,
                    "used_by": user_id,
                    "used_at": datetime.utcnow()
                }}
            )

            await message.reply_text(
                f"🎉 Gift code redeemed successfully!\n\n"
                f"⭐ You now have premium for {gift_code['premium_duration']} days!\n"
                f"⏰ Premium valid until: {end_date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                f"Enjoy your premium features! 🚀"
            )

        except Exception as e:
            await message.reply_text(f"❌ Error redeeming gift code: {str(e)}")

    @app.on_message(filters.command("giftcodes") & filters.user(ADMIN_IDS))
    async def list_gift_codes(client: Client, message: Message):
        try:
            codes = list(gift_codes_collection.find().sort("created_at", -1).limit(10))
            
            if not codes:
                await message.reply_text("No gift codes created yet.")
                return
            
            text = "🎁 Recent Gift Codes:\n\n"
            for code in codes:
                status = "✅ Used" if code["is_used"] else "🟢 Active" if code["expires_at"] > datetime.utcnow() else "❌ Expired"
                used_by = f" by user {code['used_by']}" if code["is_used"] else ""
                
                text += (
                    f"🔑 Code: `{code['code']}`\n"
                    f"⭐ Duration: {code['premium_duration']} days\n"
                    f"⏰ Valid until: {code['expires_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                    f"📊 Status: {status}{used_by}\n"
                    f"────────────────────\n"
                )
            
            await message.reply_text(text)
            
        except Exception as e:
            await message.reply_text(f"❌ Error listing gift codes: {str(e)}")
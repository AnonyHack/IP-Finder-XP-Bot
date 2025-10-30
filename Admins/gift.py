# Admins/gift.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
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
                error_text = (
                    "<b>❌ Usage Guide</b>\n\n"
                    "<blockquote>"
                    "<b>Command:</b> /giftc &lt;duration&gt; &lt;validity&gt;\n\n"
                    "<b>Example:</b>\n"
                    "/giftc 3 1h - Creates a code that gives 3 days premium, valid for 1 hour\n"
                    "/giftc 7 2d - Creates a code that gives 7 days premium, valid for 2 days"
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
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
                error_text = (
                    "<b>❌ Invalid Format</b>\n\n"
                    "<blockquote>"
                    "Please use one of these validity formats:\n"
                    "• h (hours) - Example: 1h, 24h\n"
                    "• d (days) - Example: 1d, 7d\n"
                    "• m (minutes) - Example: 30m, 60m"
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
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

            success_text = (
                "<b>🎁 Gift Code Created!</b>\n\n"
                "<blockquote>"
                f"🔑 <b>Code:</b> <code>{code}</code>\n"
                f"⭐ <b>Premium Duration:</b> {premium_duration} days\n"
                f"⏰ <b>Valid Until:</b> {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                "Share this code with users to redeem premium features!"
                "</blockquote>"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
            ])

            await message.reply_text(
                success_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:
            error_text = (
                "<b>❌ Error Creating Gift Code</b>\n\n"
                f"<blockquote>{str(e)}</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

    @app.on_message(filters.command("redeem"))
    async def redeem_gift_code(client: Client, message: Message):
        try:
            args = message.text.split()
            if len(args) < 2:
                error_text = (
                    "<b>❌ Usage Guide</b>\n\n"
                    "<blockquote>"
                    "<b>Command:</b> /redeem &lt;gift_code&gt;\n\n"
                    "<b>Example:</b>\n"
                    "/redeem ABC123XYZ456"
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                return

            code = args[1].upper()
            
            # Check if code exists and is valid
            gift_code = gift_codes_collection.find_one({"code": code, "is_used": False})
            
            if not gift_code:
                error_text = (
                    "<b>❌ Invalid Gift Code</b>\n\n"
                    "<blockquote>"
                    "This gift code is either invalid or has already been used.\n"
                    "Please check the code and try again."
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                return
            
            if gift_code["expires_at"] < datetime.utcnow():
                error_text = (
                    "<b>❌ Expired Gift Code</b>\n\n"
                    "<blockquote>"
                    "This gift code has expired and can no longer be used.\n"
                    "Please contact admin for a new code."
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
                ])
                
                await message.reply_text(
                    error_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
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
                end_date = new_end_date
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

            success_text = (
                "<b>🎉 Gift Code Redeemed Successfully!</b>\n\n"
                "<blockquote>"
                f"⭐ <b>Premium Duration:</b> {gift_code['premium_duration']} days\n"
                f"⏰ <b>Valid Until:</b> {end_date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                "Enjoy your premium features! 🚀"
                "</blockquote>"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
            ])

            await message.reply_text(
                success_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:
            error_text = (
                "<b>❌ Error Redeeming Gift Code</b>\n\n"
                f"<blockquote>{str(e)}</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

    @app.on_message(filters.command("giftcodes") & filters.user(ADMIN_IDS))
    async def list_gift_codes(client: Client, message: Message):
        try:
            codes = list(gift_codes_collection.find().sort("created_at", -1).limit(10))
            
            if not codes:
                empty_text = (
                    "<b>🎁 Gift Codes</b>\n\n"
                    "<blockquote>"
                    "No gift codes created yet.\n"
                    "Use /giftc to create your first gift code!"
                    "</blockquote>"
                )
                
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
                ])
                
                await message.reply_text(
                    empty_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                return
            
            text = "<b>🎁 Recent Gift Codes</b>\n\n<blockquote>"
            for code in codes:
                status = "✅ Used" if code["is_used"] else "🟢 Active" if code["expires_at"] > datetime.utcnow() else "❌ Expired"
                used_by = f" by user {code['used_by']}" if code["is_used"] else ""
                
                text += (
                    f"🔑 <b>Code:</b> <code>{code['code']}</code>\n"
                    f"⭐ <b>Duration:</b> {code['premium_duration']} days\n"
                    f"⏰ <b>Valid until:</b> {code['expires_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                    f"📊 <b>Status:</b> {status}{used_by}\n"
                    f"────────────────────\n"
                )
            
            text += "</blockquote>"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
            ])
            
            await message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            
        except Exception as e:
            error_text = (
                "<b>❌ Error Listing Gift Codes</b>\n\n"
                f"<blockquote>{str(e)}</blockquote>"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_gift")]
            ])
            
            await message.reply_text(
                error_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

    # Handle close button for gift messages
    @app.on_callback_query(filters.regex("close_gift"))
    async def close_gift(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Gift info closed")

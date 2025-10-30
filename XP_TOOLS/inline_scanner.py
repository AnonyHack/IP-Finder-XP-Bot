# XP_TOOLS/inline_scanner.py
from pyrogram import Client, enums, filters
from pyrogram.types import (
    InlineQuery, InlineQueryResultPhoto, InlineKeyboardMarkup,
    InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
)
import ipinfo, ipaddress
from datetime import datetime
import config

from XP_TOOLS.leaderboard import increment_search  # ✅ Import leaderboard increment function
from Admins.user_management import is_user_banned
from Admins.maintenance import check_maintenance_mode as is_maintenance_mode, get_maintenance_message


def register_inline_scanner(app: Client, db, is_user_member=None, ask_user_to_join=None):
    search_logs = db["search_logs"]
    premium_db = db["premium_users"]
    users_collection = db[config.con.USERS_COLLECTION]

    DEFAULT_SCANS = getattr(config.con, "SCANS_LIMIT", 5)
    PREMIUM_SCANS = getattr(config.con, "PREMIUM_SCANS", 50)

    @app.on_inline_query()
    async def inline_query_handler(client: Client, query: InlineQuery):
        user_id = query.from_user.id

        # ---------------- MAINTENANCE CHECK ----------------
        if await is_maintenance_mode():
            maintenance_msg = await get_maintenance_message()
            await query.answer([
                InlineQueryResultArticle(
                    title="Maintenance Mode Active",
                    input_message_content=InputTextMessageContent(
                        "<b>🚧 Maintenance Mode Active</b>\n\n"
                        "<blockquote>"
                        f"{maintenance_msg}\n\n"
                        f"⏰ Please try again later.\n"
                        f"📞 Contact: {getattr(config.con, 'BOT_DEVELOPER', 'https://t.me/Am_ItachiUchiha')} for updates"
                        "</blockquote>",
                        parse_mode=enums.ParseMode.HTML
                    ),
                    description="Bot is under maintenance",
                    thumb_url="https://img.icons8.com/fluency/48/maintenance.png"
                )
            ], cache_time=0, is_personal=True)
            return

        # ---------------- BAN CHECK ----------------
        if await is_user_banned(db, user_id):
            await query.answer([
                InlineQueryResultArticle(
                    title="Banned User",
                    input_message_content=InputTextMessageContent(
                        "<b>🚫 Account Banned</b>\n\n"
                        "<blockquote>"
                        "You have been banned from using this bot.\n"
                        "Contact admin for more information."
                        "</blockquote>",
                        parse_mode=enums.ParseMode.HTML
                    ),
                    description="You are not allowed to use this bot",
                    thumb_url="https://img.icons8.com/fluency/48/error.png"
                )
            ], cache_time=0, is_personal=True)
            return

        # ---------------- FORCE JOIN CHECK ----------------
        if is_user_member and not await is_user_member(client, user_id):
            results = [
                InlineQueryResultArticle(
                    title="Join Required Channels",
                    input_message_content=InputTextMessageContent(
                        "<b>🚨 Join Required</b>\n\n"
                        "<blockquote>"
                        "To use this bot, you must join our channels first!\n"
                        "Please start a chat with the bot to get the links."
                        "</blockquote>",
                        parse_mode=enums.ParseMode.HTML
                    ),
                    description="Click to see instructions",
                    thumb_url="https://img.icons8.com/fluency/48/error.png"
                )
            ]
            await query.answer(results, cache_time=0, is_personal=True)
            return

        username = query.from_user.username or None
        query_str = query.query.strip()

        # ---------------- PREMIUM CHECK ----------------
        premium_record = premium_db.find_one({"user_id": user_id})
        is_premium = False
        scans_limit = DEFAULT_SCANS
        if premium_record and premium_record.get("end_date", datetime.utcnow()) > datetime.utcnow():
            is_premium = True
            scans_limit = PREMIUM_SCANS

        # ---------------- SCANS LEFT ----------------
        user_record = users_collection.find_one({"user_id": user_id})
        if not user_record:
            users_collection.insert_one({"user_id": user_id, "username": username, "scans_left": scans_limit})
            scans_left = scans_limit
        else:
            scans_left = user_record.get("scans_left", scans_limit)

        if scans_left <= 0:
            results = [
                InlineQueryResultArticle(
                    title="Daily Limit Reached",
                    input_message_content=InputTextMessageContent(
                        f"<b>⚠️ Limit Reached</b>\n\n"
                        f"<blockquote>"
                        f"{'Premium' if is_premium else 'Daily'} scan limit reached ({scans_limit}).\n"
                        f"Contact admin to upgrade your plan."
                        f"</blockquote>",
                        parse_mode=enums.ParseMode.HTML
                    ),
                    description="You have no scans left",
                    thumb_url="https://img.icons8.com/fluency/48/error.png"
                )
            ]
            await query.answer(results, cache_time=0, is_personal=True)
            return

        try:
            ipdata = ipaddress.ip_address(query_str)

            # ✅ Log search
            search_logs.insert_one({
                "user_id": user_id,
                "ip": query_str,
                "timestamp": datetime.utcnow(),
                "source": "inline"
            })

            # ✅ Decrement scans_left
            users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"scans_left": -1}, "$set": {"username": username}}
            )
            scans_left -= 1

            # ✅ Increment leaderboard
            increment_search(db, user_id, username)

            access_token = config.con.IP_API
            handler = ipinfo.getHandler(access_token)
            ip = handler.getDetails(ipdata)

            x = [
                ip.details.get('ip', None), ip.details.get('country_name', None),
                ip.details.get('continent', {}).get('name', None), ip.details.get('region', None),
                ip.details.get('city', None), ip.details.get('postal', None),
                ip.details.get('timezone', None), ip.details.get('latitude', None),
                ip.details.get('longitude', None), ip.details.get('loc', None),
                ip.details.get('country_currency', {}).get('code', None),
                ip.details.get('org', None), ip.details.get('country_flag', {}).get('emoji', None)
            ]

            # Get URLs from config with fallbacks
            bot_developer = getattr(config.con, "BOT_DEVELOPER", "https://t.me/Am_ItachiUchiha")
            powered_by = getattr(config.con, "POWERED_BY", "https://t.me/XPTOOLSTEAM")
            bot_url = getattr(config.con, "BOT_URL", "https://t.me/XPToolsBot")

            # IP info message in quoted style
            caption = (
                "<b>🍀 Location Found 🔎</b>\n\n"
                "<blockquote>"
                f"🛰 <b>IP Address:</b> <code>{x[0]}</code>\n"
                f"🌎 <b>Country:</b> {x[1]} {x[12]}\n"
                f"💠 <b>Continent:</b> {x[2]}\n"
                f"🗺 <b>Province:</b> {x[3]}\n"
                f"🏠 <b>City:</b> {x[4]}\n"
                f"✉️ <b>Postal Code:</b> <code>{x[5]}</code>\n"
                f"🗼 <b>Internet Provider:</b> {x[11]}\n"
                f"🕢 <b>Time Zone:</b> {x[6]}\n"
                f"〽️ <b>Location:</b> <code>{x[9]}</code>\n"
                f"💰 <b>Currency:</b> {x[10]}\n"
                f"⏳ <b>Scans Left:</b> {scans_left}\n\n"
                f"📞 <b>Developer:</b> <a href='{bot_developer}'>Link</a>\n"
                "❗ <i>NOTE: This info is approximate and may not be 100% accurate.</i>"
                "</blockquote>"
            )

            results = [
                InlineQueryResultPhoto(
                    photo_url="https://i.ibb.co/C5x5KCdn/LG.jpg",
                    id="80100192",
                    thumb_url="https://i.ibb.co/C5x5KCdn/LG.jpg",
                    title='🌎 Inline Share Location 🔎',
                    description=f"🍀 Location Found : {x[0]}",
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=bot_developer)],
                        [InlineKeyboardButton("⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ", url=powered_by)],
                        [
                            InlineKeyboardButton("🤖 ꜱᴛᴀʀᴛ ʙᴏᴛ", url=bot_url),
                            InlineKeyboardButton("🗑️ ᴄʟᴏꜱᴇ", callback_data="close_inline")
                        ]
                    ])
                )
            ]

            await client.answer_inline_query(query.id, results=results, cache_time=2, is_personal=True)

        except ValueError:
            pass

    # Handle close button for inline results - FIXED VERSION
    @app.on_callback_query(filters.regex("close_inline"))
    async def close_inline(client, callback_query):
        try:
            # For inline messages, we need to edit the message instead of deleting it
            if callback_query.message:
                await callback_query.message.delete()
            else:
                # For inline queries, we can only edit the message to show it's closed
                await callback_query.edit_message_text(
                    "🗑️ Message closed",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🤖 ꜱᴛᴀʀᴛ ʙᴏᴛ", url=getattr(config.con, "BOT_URL", "https://t.me/XPToolsBot"))]
                    ])
                )
            await callback_query.answer("Message closed")
        except Exception as e:
            # If we can't delete or edit, just answer the callback
            await callback_query.answer("Message closed")

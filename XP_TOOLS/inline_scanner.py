# XP_TOOLS/inline_scanner.py
from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultPhoto, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
import ipinfo, ipaddress
from datetime import datetime
import config

from XP_TOOLS.leaderboard import increment_search # ✅ Import leaderboard increment function
from Admins.user_management import is_user_banned
from Admins.maintenance import is_maintenance_mode, get_maintenance_message

def register_inline_scanner(app: Client, db, is_user_member=None, ask_user_to_join=None):
    search_logs = db["search_logs"]
    premium_db = db["premium_users"]
    users_collection = db[config.con.USERS_COLLECTION]

    DEFAULT_SCANS = getattr(config.con, "SCANS_LIMIT", 2)
    PREMIUM_SCANS = getattr(config.con, "PREMIUM_SCANS", 10)

    @app.on_inline_query()
    async def inline_query_handler(client: Client, query: InlineQuery):
        user_id = query.from_user.id

        # Check if maintenance mode is active
        if await is_maintenance_mode():
            maintenance_msg = await get_maintenance_message()
            await query.answer([
                InlineQueryResultArticle(
                    title="Maintenance Mode Active",
                    input_message_content=InputTextMessageContent(
                        f"🚧 Maintenance Mode Active\n\n{maintenance_msg}\n\n"
                        f"⏰ Please try again later.\n"
                        f"📞 Contact: @Am_ItachiUchiha for updates"
                    ),
                    description="Bot is under maintenance",
                    thumb_url="https://img.icons8.com/fluency/48/maintenance.png"
                )
            ], cache_time=0, is_personal=True)
            return

        # Check if user is banned
        if await is_user_banned(db, user_id):
            await query.answer([
                InlineQueryResultArticle(
                    title="Banned User",
                    input_message_content=InputTextMessageContent(
                        "🚫 You have been banned from using this bot."
                    ),
                    description="You are not allowed to use this bot",
                    thumb_url="https://img.icons8.com/fluency/48/error.png"
                )
            ], cache_time=0, is_personal=True)
            return

        # Check if user is member of required channels
        if is_user_member and not await is_user_member(client, user_id):
            # Can't send messages in inline mode, so show error result
            results = [
                InlineQueryResultArticle(
                    title="Join Required Channels",
                    input_message_content=InputTextMessageContent(
                        "🚨 To use this bot, you must join our channels first! "
                        "Please start a chat with the bot to get the links."
                    ),
                    description="Click to see instructions",
                    thumb_url="https://img.icons8.com/fluency/48/error.png"
                )
            ]
            await query.answer(results, cache_time=0, is_personal=True)
            return
            
        username = query.from_user.username or None
        query_str = query.query.strip()

        # ------------------ PREMIUM CHECK ------------------
        premium_record = premium_db.find_one({"user_id": user_id})
        is_premium = False
        scans_limit = DEFAULT_SCANS
        if premium_record and premium_record.get("end_date", datetime.utcnow()) > datetime.utcnow():
            is_premium = True
            scans_limit = PREMIUM_SCANS

        # ------------------ SCANS LEFT CHECK ------------------
        user_record = users_collection.find_one({"user_id": user_id})
        if not user_record:
            # Create record if not exists
            users_collection.insert_one({"user_id": user_id, "username": username, "scans_left": scans_limit})
            scans_left = scans_limit
        else:
            scans_left = user_record.get("scans_left", scans_limit)

        if scans_left <= 0:
            results = [
                InlineQueryResultArticle(
                    title="Daily Limit Reached",
                    input_message_content=InputTextMessageContent(
                        f"⚠️ {'Premium' if is_premium else 'Daily'} scan limit reached ({scans_limit})."
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
            scans_left -= 1  # local variable for immediate display

            # ✅ Increment leaderboard search count
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

            results = [
                InlineQueryResultPhoto(
                    photo_url="https://telegra.ph/file/dba626143ccfea3c4d718.jpg",
                    id="80100192",
                    thumb_url="https://telegra.ph/file/dba626143ccfea3c4d718.jpg",
                    title='🌎 Inline Share Location 🔎',
                    description=f"🍀 Location Found : {x[0]}",
                    caption=f"🍀 Location Found 🔎\n\n"
                            f"🛰IP Address ➤ {x[0]}\n"
                            f"🌎Country ➤ {x[1]}{x[12]}\n"
                            f"💠Continent ➤ {x[2]}\n"
                            f"🗺Province ➤ {x[3]}\n"
                            f"🏠City ➤ {x[4]}\n"
                            f"✉️ Postal Code ➤ <code>{x[5]}</code>\n"
                            f"🗼Internet Provider ➤ {x[11]}\n"
                            f"🕢Time Zone ➤ {x[6]}\n"
                            f"〽️Location ➤ <code>{x[9]}</code>\n"
                            f"💰 Currency ➤ {x[10]}\n\n"
                            f"🔥Powered By @Megahubbots 🇱🇰\n"
                            f"⏳ Scans Left: {scans_left}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('‍🔥Megahubbots', url='https://t.me/Megahubbots')],
                        [InlineKeyboardButton('🤖 IP ҒIΠDΣR BOT 🔎', url='https://t.me/IpTrackerxpbot')]
                    ])
                )
            ]

            await client.answer_inline_query(query.id, results=results, cache_time=2, is_personal=True)

        except ValueError:
            pass
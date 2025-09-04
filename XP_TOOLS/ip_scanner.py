# XP_TOOLS/ip_scanner.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import ipinfo, ipaddress, requests
from datetime import datetime
import config
from XP_TOOLS.leaderboard import increment_search
from Admins.user_management import is_user_banned
from Admins.maintenance import check_maintenance_mode as is_maintenance_mode, get_maintenance_message

def register_ip_scanner(app: Client, db, is_user_member=None, ask_user_to_join=None):
    ip_data = {}
    search_logs = db["search_logs"]
    premium_db = db["premium_users"]
    users_collection = db[config.con.USERS_COLLECTION]

    DEFAULT_SCANS = getattr(config.con, "SCANS_LIMIT", 5)
    PREMIUM_SCANS = getattr(config.con, "PREMIUM_SCANS", 50)

    # NOTE: exclude commands from this handler using regex 
    @app.on_message(filters.text & filters.private & ~filters.regex(r"^/"))
    async def get_ip(client: Client, message: Message):
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
            
        username = message.from_user.username or None

        # ------------------ PREMIUM CHECK ------------------
        premium_record = premium_db.find_one({"user_id": user_id})
        is_premium = False
        scans_limit = DEFAULT_SCANS
        if premium_record and premium_record.get("end_date", datetime.utcnow()) > datetime.utcnow():
            is_premium = True
            scans_limit = PREMIUM_SCANS

        # ------------------ DAILY LIMIT CHECK ------------------
        user_record = users_collection.find_one({"user_id": user_id})
        if not user_record:
            # Create record if not exists
            users_collection.insert_one({"user_id": user_id, "username": username, "scans_left": scans_limit})
            scans_left = scans_limit
        else:
            scans_left = user_record.get("scans_left", scans_limit)

        if scans_left <= 0:
            await message.reply_text(
                f"⚠️ {'Premium' if is_premium else 'Daily'} scan limit reached ({scans_limit})."
            )
            return

        ip_address = message.text
        try:
            ip = ipaddress.ip_address(ip_address)

            # ✅ Log search
            search_logs.insert_one({
                "user_id": user_id,
                "ip": ip_address,
                "timestamp": datetime.utcnow(),
                "source": "private"
            })

            # ✅ Increment leaderboard search count
            increment_search(db, user_id, username)

            # ✅ Decrement scans_left
            users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"scans_left": -1}, "$set": {"username": username}}
            )
            scans_left -= 1  # local variable for immediate feedback

            await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)

            access_token = config.con.IP_API
            handler = ipinfo.getHandler(access_token)
            ip = handler.getDetails(ip_address)

            x = [
                ip.details.get('ip', None), ip.details.get('country_name', None),
                ip.details.get('continent', {}).get('name', None), ip.details.get('region', None),
                ip.details.get('city', None), ip.details.get('postal', None),
                ip.details.get('timezone', None), ip.details.get('latitude', None),
                ip.details.get('longitude', None), ip.details.get('loc', None),
                ip.details.get('country_currency', {}).get('code', None), ip.details.get('org', None),
                ip.details.get('country_flag', {}).get('emoji', None)
            ]

            # Inline buttons
            inline_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    '✈️ Open Google Map 🌎',
                    url=f'https://www.google.com/maps/search/?api=1&query={x[7]}%2C{x[8]}')],
                [InlineKeyboardButton('🤖 IP ҒIΠDΣR BOT', url=config.con.BOT_URL)]
            ])

            # Generate map image URL
            url = f"https://maps.locationiq.com/v3/staticmap?key=pk.{'YOUR API KEY'}&center={x[7]},{x[8]}&zoom=16&size=600x600&markers=icon:large-blue-cutout%7C{x[7]},{x[8]}"
            ip_data[message.chat.id] = {'ip_address': x[0]}

            try:
                response = requests.get(url)
                response.raise_for_status()
                await app.send_photo(
                    chat_id=message.chat.id,
                    photo=url,
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
                    reply_markup=inline_keyboard
                )
            except:
                await app.send_message(
                    chat_id=message.chat.id,
                    text=f"🍀 Location Found 🔎\n\n"
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
                    reply_markup=inline_keyboard
                )
        except ValueError:
            return

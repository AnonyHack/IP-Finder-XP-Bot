from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config
import pymongo
from datetime import datetime, timedelta
import time
import requests

# MongoDB setup
mongo_client = pymongo.MongoClient(config.con.MONGO_URI)
db = mongo_client[config.con.MONGO_DB]
users_collection = db[config.con.USERS_COLLECTION]
search_logs = db["search_logs"]
payments = db["payments"]
gift_codes_collection = db["gift_codes"]

# Record bot start time
BOT_START = time.time()


def register_stats_handler(app: Client):
    @app.on_message(filters.command("stats"))
    async def stats_handler(client: Client, message: Message):
        user_id = message.from_user.id
        if user_id not in config.con.ADMIN_USER_IDS:
            return

        # Send loading message and show main dashboard
        sent_message = await message.reply_text("📊 Loading statistics...")
        await show_main_dashboard(client, sent_message)

    async def show_main_dashboard(client, message):
        # --------------------- BOT UPTIME ---------------------
        uptime_seconds = int(time.time() - BOT_START)
        uptime = str(timedelta(seconds=uptime_seconds))

        # --------------------- PING ---------------------
        try:
            ping_start = time.time()
            requests.get("https://www.google.com", timeout=5)
            ping_ms = int((time.time() - ping_start) * 1000)
        except:
            ping_ms = -1

        # --------------------- USER STATS ---------------------
        now = datetime.utcnow()
        today_24h = now - timedelta(days=1)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)

        total_users = users_collection.count_documents({})
        today_joins = users_collection.count_documents({"joined_at": {"$gte": today_24h}})
        last_7d_joins = users_collection.count_documents({"joined_at": {"$gte": last_7d}})
        last_30d_joins = users_collection.count_documents({"joined_at": {"$gte": last_30d}})

        # Main dashboard text with stylish formatting
        text = (
            "⍟─────[ ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs ]─────⍟\n\n"
            "<blockquote>"
            f"‣ ʙᴏᴛ ᴜᴘᴛɪᴍᴇ: {uptime} ⏱️\n"
            f"‣ ᴘɪɴɢ (ɢᴏᴏɢʟᴇ): {ping_ms} ms 🌐\n\n"
            
            f"👥 ᴜsᴇʀ sᴛᴀᴛɪsᴛɪᴄs:\n"
            f"‣ ᴛᴏᴛᴀʟ ᴜsᴇʀs: {total_users} 👤\n"
            f"‣ ᴛᴏᴅᴀʏ's ᴊᴏɪɴs: {today_joins} 🆕\n"
            f"‣ 7-ᴅᴀʏ ᴊᴏɪɴs: {last_7d_joins} 📅\n"
            f"‣ 30-ᴅᴀʏ ᴊᴏɪɴs: {last_30d_joins} 🗓️\n"
            "</blockquote>"
            "⍟─────────────────────────⍟"
        )

        # Navigation buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔍 Searches", callback_data="stats_searches"),
                InlineKeyboardButton("💰 Payments", callback_data="stats_payments")
            ],
            [
                InlineKeyboardButton("🎁 Gifts", callback_data="stats_gifts"),
                InlineKeyboardButton("❌ Close", callback_data="close_stats")
            ]
        ])

        await message.edit_text(text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)

    async def show_search_stats(client, message):
        # --------------------- SEARCH STATS ---------------------
        today_date = datetime.utcnow().date()
        tomorrow = today_date + timedelta(days=1)

        today_searches = search_logs.count_documents({
            "timestamp": {"$gte": datetime(today_date.year, today_date.month, today_date.day),
                          "$lt": datetime(tomorrow.year, tomorrow.month, tomorrow.day)}
        })
        private_searches = search_logs.count_documents({
            "timestamp": {"$gte": datetime(today_date.year, today_date.month, today_date.day),
                          "$lt": datetime(tomorrow.year, tomorrow.month, tomorrow.day)},
            "source": "private"
        })
        inline_searches = search_logs.count_documents({
            "timestamp": {"$gte": datetime(today_date.year, today_date.month, today_date.day),
                          "$lt": datetime(tomorrow.year, tomorrow.month, tomorrow.day)},
            "source": "inline"
        })

        text = (
            "⍟─────[ sᴇᴀʀᴄʜ sᴛᴀᴛɪsᴛɪᴄs ]─────⍟\n\n"
            "<blockquote>"
            f"🔍 ᴛᴏᴅᴀʏ's sᴇᴀʀᴄʜᴇs:\n"
            f"‣ ᴛᴏᴛᴀʟ: {today_searches} 📊\n"
            f"‣ ᴘʀɪᴠᴀᴛᴇ: {private_searches} 💬\n"
            f"‣ ɪɴʟɪɴᴇ: {inline_searches} 🔗\n\n"
            
            f"📈 sᴇᴀʀᴄʜ ᴏᴠᴇʀᴠɪᴇᴡ:\n"
            f"‣ ᴘʀɪᴠᴀᴛᴇ ʀᴀᴛᴇ: {round((private_searches/today_searches)*100, 2) if today_searches > 0 else 0}%\n"
            f"‣ ɪɴʟɪɴᴇ ʀᴀᴛᴇ: {round((inline_searches/today_searches)*100, 2) if today_searches > 0 else 0}%"
            "</blockquote>"
            "⍟─────────────────────────⍟"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="stats_main")],
            [InlineKeyboardButton("❌ Close", callback_data="close_stats")]
        ])

        await message.edit_text(text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)

    async def show_payment_stats(client, message):
        # --------------------- PAYMENT STATS ---------------------
        now = datetime.utcnow()
        today_24h = now - timedelta(days=1)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)

        total_payments = payments.count_documents({})
        total_revenue_cursor = list(payments.aggregate([{"$group": {"_id": None, "sum": {"$sum": "$amount"}}}]))
        total_revenue_val = total_revenue_cursor[0]["sum"] if total_revenue_cursor else 0

        today_payments = payments.count_documents({"timestamp": {"$gte": today_24h}})
        today_revenue_cursor = list(payments.aggregate([
            {"$match": {"timestamp": {"$gte": today_24h}}},
            {"$group": {"_id": None, "sum": {"$sum": "$amount"}}}
        ]))
        today_revenue_val = today_revenue_cursor[0]["sum"] if today_revenue_cursor else 0

        last_7d_payments = payments.count_documents({"timestamp": {"$gte": last_7d}})
        last_7d_revenue_cursor = list(payments.aggregate([
            {"$match": {"timestamp": {"$gte": last_7d}}},
            {"$group": {"_id": None, "sum": {"$sum": "$amount"}}}
        ]))
        last_7d_revenue_val = last_7d_revenue_cursor[0]["sum"] if last_7d_revenue_cursor else 0

        last_30d_payments = payments.count_documents({"timestamp": {"$gte": last_30d}})
        last_30d_revenue_cursor = list(payments.aggregate([
            {"$match": {"timestamp": {"$gte": last_30d}}},
            {"$group": {"_id": None, "sum": {"$sum": "$amount"}}}
        ]))
        last_30d_revenue_val = last_30d_revenue_cursor[0]["sum"] if last_30d_revenue_cursor else 0

        text = (
            "⍟─────[ ᴘᴀʏᴍᴇɴᴛ sᴛᴀᴛɪsᴛɪᴄs ]─────⍟\n\n"
            "<blockquote>"
            f"💰 ᴘᴀʏᴍᴇɴᴛ ᴏᴠᴇʀᴠɪᴇᴡ:\n"
            f"‣ ᴛᴏᴛᴀʟ ᴘᴀʏᴍᴇɴᴛs: {total_payments} 💳\n"
            f"‣ ᴛᴏᴛᴀʟ ʀᴇᴠᴇɴᴜᴇ: {total_revenue_val} ⭐️\n\n"
            
            f"📊 ʀᴇᴄᴇɴᴛ ᴘᴀʏᴍᴇɴᴛs:\n"
            f"‣ ᴛᴏᴅᴀʏ: {today_payments} | {today_revenue_val} ⭐️\n"
            f"‣ 7-ᴅᴀʏs: {last_7d_payments} | {last_7d_revenue_val} ⭐️\n"
            f"‣ 30-ᴅᴀʏs: {last_30d_payments} | {last_30d_revenue_val} ⭐️\n\n"
            
            f"📈 ᴀᴠᴇʀᴀɢᴇ ʀᴇᴠᴇɴᴜᴇ:\n"
            f"‣ ᴘᴇʀ ᴘᴀʏᴍᴇɴᴛ: {round(total_revenue_val/total_payments, 2) if total_payments > 0 else 0} ⭐️"
            "</blockquote>"
            "⍟─────────────────────────⍟"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="stats_main")],
            [InlineKeyboardButton("❌ Close", callback_data="close_stats")]
        ])

        await message.edit_text(text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)

    async def show_gift_stats(client, message):
        # --------------------- GIFT CODE STATS ---------------------
        total_gift_codes = gift_codes_collection.count_documents({})
        used_gift_codes = gift_codes_collection.count_documents({"is_used": True})
        active_gift_codes = total_gift_codes - used_gift_codes

        text = (
            "⍟─────[ ɢɪғᴛ ᴄᴏᴅᴇ sᴛᴀᴛɪsᴛɪᴄs ]─────⍟\n\n"
            "<blockquote>"
            f"🎁 ɢɪғᴛ ᴄᴏᴅᴇs ᴏᴠᴇʀᴠɪᴇᴡ:\n"
            f"‣ ᴛᴏᴛᴀʟ ᴄᴏᴅᴇs: {total_gift_codes} 🎫\n"
            f"‣ ᴜsᴇᴅ ᴄᴏᴅᴇs: {used_gift_codes} ✅\n"
            f"‣ ᴀᴄᴛɪᴠᴇ ᴄᴏᴅᴇs: {active_gift_codes} 🔄\n\n"
            
            f"📊 ᴜsᴀɢᴇ sᴛᴀᴛs:\n"
            f"‣ ᴜsᴀɢᴇ ʀᴀᴛᴇ: {round((used_gift_codes/total_gift_codes)*100, 2) if total_gift_codes > 0 else 0}%\n"
            f"‣ ᴀᴠᴀɪʟᴀʙʟᴇ: {round((active_gift_codes/total_gift_codes)*100, 2) if total_gift_codes > 0 else 0}%"
            "</blockquote>"
            "⍟─────────────────────────⍟"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="stats_main")],
            [InlineKeyboardButton("❌ Close", callback_data="close_stats")]
        ])

        await message.edit_text(text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)

    # Callback query handlers
    @app.on_callback_query(filters.regex("^stats_"))
    async def handle_stats_navigation(client, callback_query):
        page = callback_query.data.split("_")[1]
        
        await callback_query.answer()
        
        if page == "main":
            await show_main_dashboard(client, callback_query.message)
        elif page == "searches":
            await show_search_stats(client, callback_query.message)
        elif page == "payments":
            await show_payment_stats(client, callback_query.message)
        elif page == "gifts":
            await show_gift_stats(client, callback_query.message)

    @app.on_callback_query(filters.regex("close_stats"))
    async def close_stats(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Statistics closed")

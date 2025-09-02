from pyrogram import Client, filters
from pyrogram.types import Message
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
payments = db["payments"]  # will be created automatically when first document is inserted

# Record bot start time
BOT_START = time.time()


def register_stats_handler(app: Client):
    @app.on_message(filters.command("stats"))
    async def stats_handler(client: Client, message: Message):
        user_id = message.from_user.id
        if user_id not in config.con.ADMIN_USER_IDS:
            return

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

        # --------------------- PAYMENT STATS ---------------------
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

        # --------------------- SEND DASHBOARD ---------------------
        await message.reply_text(
            f"📊 ADMIN DASHBOARD | STATISTICS\n"
            f"⏱️ Bot Uptime: {uptime}\n"
            f"🌐 Ping (Google): {ping_ms} ms\n\n"

            f"👥 User Statistics:\n"
            f"• Total Users: {total_users}\n"
            f"• Today Joins: {today_joins}\n"
            f"• 7-Day Joins: {last_7d_joins}\n"
            f"• 30-Day Joins: {last_30d_joins}\n\n"

            f"🔍 Search Statistics:\n"
            f"• Today's Searches: {today_searches}\n"
            f"   ├ Private: {private_searches}\n"
            f"   └ Inline: {inline_searches}\n\n"

            f"💰 Payment Statistics:\n"
            f"• Total Payments: {total_payments} | Revenue: {total_revenue_val} ⭐️\n"
            f"• Today: {today_payments} payments | {today_revenue_val} ⭐️\n"
            f"• 7-Days: {last_7d_payments} payments | {last_7d_revenue_val} ⭐️\n"
            f"• 30-Days: {last_30d_payments} payments | {last_30d_revenue_val} ⭐️"
        )

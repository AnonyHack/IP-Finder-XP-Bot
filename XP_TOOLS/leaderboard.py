# XP_TOOLS/leaderboard.py
from pyrogram import Client, filters
from pyrogram.types import Message
import pymongo
from pymongo.database import Database  # <--- add this

# Expose command metadata
COMMANDS = [("leaderboard", " 📊 View Leaderboard")]

def register_leaderboard_handler(app: Client, db: Database):  # use Database here
    users_collection = db["users"]

    # /leaderboard command
    @app.on_message(filters.command("leaderboard"))
    async def leaderboard_handler(client: Client, message: Message):
        leaderboard = list(users_collection.find(
            {"searches": {"$gt": 0}},
            {"_id": 0, "user_id": 1, "username": 1, "searches": 1}
        ).sort("searches", -1).limit(10))

        if not leaderboard:
            await message.reply("📊 Leaderboard is empty!")
            return

        text = "🏆 **Top 10 Users by Searches** 🏆\n\n"
        for i, user in enumerate(leaderboard, start=1):
            username = f"@{user['username']}" if user.get("username") else f"User {user['user_id']}"
            searches = user.get("searches", 0)
            text += f"**{i}. {username}** → {searches} searches\n"

        await message.reply(text)


# Call this inside scanner files after a successful scan
def increment_search(db: Database, user_id: int, username: str):
    users_collection = db["users"]
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"username": username}, "$inc": {"searches": 1}},
        upsert=True
    )

# XP_TOOLS/leaderboard.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import pymongo
from pymongo.database import Database

from imagen import send_notification


def register_leaderboard_handler(app: Client, db: Database):
    users_collection = db["users"]

    # /leaderboard command
    @app.on_message(filters.command("leaderboard"))
    async def leaderboard_handler(client: Client, message: Message):
        # Get total number of users with searches
        total_users = users_collection.count_documents({"searches": {"$gt": 0}})

                # Send a notification after user starts the bot
        try:
            username = message.from_user.username or "NoUsername"
            await send_notification(client, message.from_user.id, username, "Checked Leaderboard")
        except Exception as e:
            print(f"Notification failed: {e}")  # Don't break the bot if notification fails

        
        if total_users == 0:
            await message.reply(
                "<b>🏆 Leaderboard</b>\n\n"
                "<blockquote>"
                "The leaderboard is currently empty!\n"
                "Be the first to make some searches and get on the board!"
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            return

        # Calculate total pages
        total_pages = (total_users + 9) // 10  # 10 users per page
        
        # Show first page - send a new message instead of editing the command
        sent_message = await message.reply_text("📊 Loading leaderboard...")
        await show_leaderboard_page(client, sent_message, 1, total_pages, total_users, users_collection)

    # Function to show leaderboard page
    async def show_leaderboard_page(client, message, page: int, total_pages: int, total_users: int, users_collection):
        skip_count = (page - 1) * 10
        leaderboard = list(users_collection.find(
            {"searches": {"$gt": 0}},
            {"_id": 0, "user_id": 1, "username": 1, "searches": 1}
        ).sort("searches", -1).skip(skip_count).limit(10))

        # Build the leaderboard text in quoted style
        text = "<b>🏆 Top Users by Searches 🏆</b>\n\n"
        text += "<blockquote>"
        
        for i, user in enumerate(leaderboard, start=skip_count + 1):
            username = f"@{user['username']}" if user.get("username") else f"User {user['user_id']}"
            searches = user.get("searches", 0)
            medal = get_medal_emoji(i)
            text += f"{medal} <b>{i}. {username}</b>\n"
            text += f"   🔍 <code>{searches}</code> searches\n\n"
        
        text += f"📄 Page {page}/{total_pages}\n"
        text += f"👥 Total Users: {total_users}\n"
        text += "</blockquote>"

        # Build pagination buttons
        buttons = []
        
        # Previous button
        if page > 1:
            buttons.append(InlineKeyboardButton("⌫ ᴘʀᴇᴠɪᴏᴜꜱ", callback_data=f"lb_prev_{page-1}"))
        
        # Next button
        if page < total_pages:
            buttons.append(InlineKeyboardButton("⌦ ɴᴇxᴛ", callback_data=f"lb_next_{page+1}"))

        # Add close button
        close_button = [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_leaderboard")]
        
        # Create keyboard layout
        keyboard = []
        if buttons:  # Only add pagination row if there are buttons
            keyboard.append(buttons)
        keyboard.append(close_button)

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Always use edit_text for the sent message
        await message.edit_text(text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)

    # Helper function to get medal emojis
    def get_medal_emoji(position: int) -> str:
        if position == 1:
            return "🥇"
        elif position == 2:
            return "🥈"
        elif position == 3:
            return "🥉"
        else:
            return "🔸"

    # Handle pagination callbacks
    @app.on_callback_query(filters.regex(r"^lb_(prev|next)_(\d+)$"))
    async def handle_leaderboard_pagination(client, callback_query):
        action = callback_query.data.split("_")[1]  # prev or next
        page = int(callback_query.data.split("_")[2])
        
        # Get total number of users with searches
        total_users = users_collection.count_documents({"searches": {"$gt": 0}})
        total_pages = (total_users + 9) // 10
        
        await callback_query.answer()
        await show_leaderboard_page(client, callback_query.message, page, total_pages, total_users, users_collection)

    # Handle close button
    @app.on_callback_query(filters.regex("close_leaderboard"))
    async def close_leaderboard(client, callback_query):
        await callback_query.message.delete()
        await callback_query.answer("Leaderboard closed")

# Call this inside scanner files after a successful scan
def increment_search(db: Database, user_id: int, username: str):
    users_collection = db["users"]
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"username": username}, "$inc": {"searches": 1}},
        upsert=True
    )

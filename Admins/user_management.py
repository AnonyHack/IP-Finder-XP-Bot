# Admins/user_management.py
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import config

def register_user_management_commands(app: Client, db, ADMIN_IDS):
    users_collection = db[config.con.USERS_COLLECTION]
    banned_users_collection = db["banned_users"]
    premium_db = db["premium_users"]
    search_logs = db["search_logs"]
    
    # Create collections if they don't exist
    if "banned_users" not in db.list_collection_names():
        db.create_collection("banned_users")

    async def is_user_banned(user_id):
        """Check if user is banned"""
        return banned_users_collection.find_one({"user_id": user_id}) is not None

    # ------------- /ban command -------------
    @app.on_message(filters.command("ban") & filters.user(ADMIN_IDS))
    async def ban_user_command(client: Client, message: Message):
        """Ban a user from using the bot with enhanced features"""
        try:
            args = message.text.split()
            if len(args) != 2:
                await message.reply_text(
                    "⚡ **IP Finder Admin Panel - Ban User**\n\n"
                    "**Usage**: /ban [user_id]\n\n"
                    "▸ **Format**: `123456789`\n"
                    "▸ **Note**: User will lose all bot access\n\n"
                    "✘ Type **'cancel'** to abort",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return

            if args[1].lower() == "cancel":
                await message.reply_text("❌ Ban cancelled.")
                return

            user_id = args[1].strip()
            
            if not user_id.isdigit():
                await message.reply_text(
                    "❌ **Invalid Input**\n\n"
                    "User ID must contain only numbers\n"
                    "**Example**: `123456789`",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return

            user_id = int(user_id)
            
            # Check if user exists
            user_data = users_collection.find_one({"user_id": user_id})
            if not user_data:
                await message.reply_text("❌ User not found in database.")
                return
            
            # Check if user is already banned
            if await is_user_banned(user_id):
                await message.reply_text(
                    f"⚠️ **User Already Banned**\n\n"
                    f"User `{user_id}` is already in ban list",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return
            
            # Get user info
            try:
                user = await client.get_users(user_id)
                username = f"@{user.username}" if user.username else user.first_name
            except:
                username = "Unknown"
            
            # Add to banned users
            banned_users_collection.insert_one({
                "user_id": user_id,
                "username": username,
                "banned_by": message.from_user.id,
                "banned_at": datetime.utcnow(),
                "reason": "Violation of Terms"
            })
            
            # Remove premium if user has it
            premium_db.delete_one({"user_id": user_id})
            
            # Enhanced ban notification to user
            try:
                appeal_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📩 Appeal Ban", url="https://t.me/Am_ItachiUchiha")],
                    [InlineKeyboardButton("📋 View Terms", callback_data="ban_terms")]
                ])

                await client.send_message(
                    user_id,
                    f"⛔ **Account Suspended**\n\n"
                    f"Your access to **IP Finder Bot** has been restricted.\n\n"
                    f"▸ **Reason**: Violation of Terms\n"
                    f"▸ **Appeal**: Available via button below\n"
                    f"▸ **Status**: Permanent (until appeal)\n\n"
                    f"⚠️ Attempting to bypass will result in IP blacklist",
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=appeal_markup
                )
                notified_success = True
            except Exception as e:
                print(f"Ban notification error: {e}")
                notified_success = False
            
            # Enhanced admin confirmation
            await message.reply_text(
                f"✅ **User Banned Successfully**\n\n"
                f"▸ **User ID**: `{user_id}`\n"
                f"▸ **Action**: Full service restriction\n"
                f"▸ **Notified**: {'Yes' if notified_success else 'Failed'}\n\n"
                f"📝 _This user has been added to ban database_",
                parse_mode=enums.ParseMode.MARKDOWN
            )
                
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")

    # ------------- /unban command -------------
    @app.on_message(filters.command("unban") & filters.user(ADMIN_IDS))
    async def unban_user_command(client: Client, message: Message):
        """Unban a user with enhanced features"""
        try:
            args = message.text.split()
            if len(args) != 2:
                await message.reply_text(
                    "⚡ **IP Finder Admin Panel - Unban User**\n\n"
                    "**Usage**: /unban [user_id]\n\n"
                    "▸ Will restore all services\n"
                    "▸ Automatic notification sent\n\n"
                    "✘ Type **'cancel'** to abort",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return

            if args[1].lower() == "cancel":
                await message.reply_text("❌ Unban cancelled.")
                return

            user_id = args[1].strip()
            
            if not user_id.isdigit():
                await message.reply_text(
                    "❌ **Invalid Input**\n\n"
                    "User ID must contain only numbers\n"
                    "**Example**: `987654321`",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return

            user_id = int(user_id)
            
            # Check if user is banned
            banned_user = banned_users_collection.find_one({"user_id": user_id})
            if not banned_user:
                await message.reply_text(
                    f"ℹ️ **User Not Banned**\n\n"
                    f"User `{user_id}` isn't in ban records",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return
            
            # Remove from banned users
            banned_users_collection.delete_one({"user_id": user_id})
            
            username = banned_user.get("username", "Unknown")
            
            # Premium unban notification
            try:
                await client.send_message(
                    user_id,
                    f"✅ **Account Reinstated**\n\n"
                    f"Your **IP Finder Bot** access has been restored!\n\n"
                    f"▸ **All services**: Reactivated\n"
                    f"▸ **Search history**: Preserved\n"
                    f"▸ **Premium status**: Unaffected\n\n"
                    f"⚠️ Please review our terms to avoid future issues",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                notified_success = True
            except Exception as e:
                print(f"Unban notification error: {e}")
                notified_success = False
            
            # Admin confirmation with flair
            await message.reply_text(
                f"✨ **User Unbanned Successfully**\n\n"
                f"▸ **User ID**: `{user_id}`\n"
                f"▸ **Services**: Reactivated\n"
                f"▸ **Notified**: {'Yes' if notified_success else 'Failed'}\n\n"
                f"📝 _Removed from ban database_",
                parse_mode=enums.ParseMode.MARKDOWN
            )
                
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")

    # ------------- /deleteuser command -------------
    @app.on_message(filters.command("deleteuser") & filters.user(ADMIN_IDS))
    async def delete_user_command(client: Client, message: Message):
        """Completely delete a user from the database"""
        try:
            args = message.text.split()
            if len(args) != 2:
                await message.reply_text(
                    "⚡ **IP Finder Admin Panel - Delete User**\n\n"
                    "**Usage**: /deleteuser [user_id]\n\n"
                    "▸ **Warning**: This action is irreversible!\n"
                    "▸ **Removes**: All user data permanently\n\n"
                    "✘ Type **'cancel'** to abort",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return

            if args[1].lower() == "cancel":
                await message.reply_text("❌ Deletion cancelled.")
                return

            user_id = args[1].strip()
            
            if not user_id.isdigit():
                await message.reply_text(
                    "❌ **Invalid Input**\n\n"
                    "User ID must contain only numbers\n"
                    "**Example**: `123456789`",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return

            user_id = int(user_id)
            
            # Get user info before deletion
            user_data = users_collection.find_one({"user_id": user_id})
            if not user_data:
                await message.reply_text("❌ User not found in database.")
                return
            
            try:
                user = await client.get_users(user_id)
                username = f"@{user.username}" if user.username else user.first_name
            except:
                username = "Unknown"
            
            # Delete user from all collections
            users_collection.delete_one({"user_id": user_id})
            banned_users_collection.delete_one({"user_id": user_id})
            premium_db.delete_one({"user_id": user_id})
            
            # Delete user's search logs
            search_logs.delete_many({"user_id": user_id})
            
            await message.reply_text(
                f"🗑️ **User Completely Deleted**\n\n"
                f"▸ **User**: {username}\n"
                f"▸ **ID**: `{user_id}`\n"
                f"▸ **Time**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                f"✅ **Removed from**: users, banned_users, premium_users, search_logs\n\n"
                f"⚠️ _This action cannot be undone_",
                parse_mode=enums.ParseMode.MARKDOWN
            )
                
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")

    # ------------- /bannedlist command -------------
    @app.on_message(filters.command("bannedlist") & filters.user(ADMIN_IDS))
    async def list_banned_users_command(client: Client, message: Message):
        """List all banned users with enhanced formatting"""
        try:
            banned_users = list(banned_users_collection.find().sort("banned_at", -1).limit(50))
            
            if not banned_users:
                await message.reply_text(
                    "🛡️ **Ban List Status**\n\n"
                    "No users currently restricted\n\n"
                    "▸ **Database**: 0 Entries\n"
                    "▸ **Last ban**: None",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return
            
            # Enhanced list formatting
            msg = [
                "⛔ **IP Finder Bot Ban List**\n",
                f"▸ **Total Banned**: {len(banned_users)}",
                f"▸ **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
                "━━━━━━━━━━━━━━━━━━━━"
            ]
            
            # Paginate if more than 10 banned users
            if len(banned_users) > 10:
                msg.append("\n**Showing first 10 entries:**\n")
                banned_users = banned_users[:10]
            
            for i, user in enumerate(banned_users, 1):
                username = user.get("username", f"User {user['user_id']}")
                ban_date = user["banned_at"].strftime("%Y-%m-%d") if "banned_at" in user else "Unknown"
                msg.append(f"{i}. {username} (`{user['user_id']}`) - {ban_date}")
            
            msg.append("\n🔍 Use /ban [ID] or /unban [ID] for actions")
            
            await message.reply_text("\n".join(msg), parse_mode=enums.ParseMode.MARKDOWN)
            
        except Exception as e:
            await message.reply_text(f"❌ Error: {str(e)}")

    # ------------- Ban terms callback handler -------------
    @app.on_callback_query(filters.regex("ban_terms"))
    async def show_ban_terms(client, callback_query):
        """Show the policy message when View Terms is clicked"""
        try:
            policy_text = """
📜 **Bot Usage Policy & Guidelines** 📜
━━━━━━━━━━━━━━━━━━━━

🔹 **1. Acceptable Use**
   ├ ✅ Permitted: Legal, non-harmful content
   └ ❌ Prohibited: Spam, harassment, illegal material

🔹 **2. Fair Usage Policy**
   ├ ⚖️ Abuse may lead to restrictions
   └ 📊 Excessive usage may be rate-limited

🔹 **3. Privacy Commitment**
   ├ 🔒 Your data stays confidential
   └ 🤝 Never shared with third parties

🔹 **4. Platform Compliance**
   ├ ✋ Must follow Telegram's Terms of Service
   └ 🌐 All content must be legal in your jurisdiction

⚠️ **Consequences of Violation**
   ├ ⚠️ First offense: Warning
   ├ 🔇 Repeated violations: Temporary suspension
   └ 🚫 Severe cases: Permanent ban

📅 _Last updated: {update_date}_
━━━━━━━━━━━━━━━━━━━━
💡 Need help? Contact @Am_ItachiUchiha
""".format(update_date=datetime.now().strftime('%Y-%m-%d'))

            await callback_query.answer()
            await callback_query.message.reply_text(policy_text, parse_mode=enums.ParseMode.MARKDOWN)
            
        except Exception as e:
            print(f"Error showing ban terms: {e}")
            await callback_query.answer("⚠️ Failed to load terms", show_alert=True)

    # ------------- Middleware to check if user is banned -------------
    @app.on_message(filters.private & ~filters.user(ADMIN_IDS))
    async def check_banned_user(client: Client, message: Message):
        """Check if user is banned before processing any message"""
        user_id = message.from_user.id
        
        if await is_user_banned(user_id):
            # User is banned, don't process the message
            try:
                await message.reply_text(
                    "🚫 **Account Suspended**\n\n"
                    "You have been banned from using this bot.\n\n"
                    "If you think this is a mistake, please contact the admin @Am_ItachiUchiha",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
            except:
                pass
            return True  # Stop further processing
        
        return False  # Continue processing

# Export the is_user_banned function for use in other modules
async def is_user_banned(db, user_id):
    """Check if user is banned"""
    banned_users_collection = db["banned_users"]
    return banned_users_collection.find_one({"user_id": user_id}) is not None

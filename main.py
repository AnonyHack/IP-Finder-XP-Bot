# main.py
from pyrogram import Client
import logging
import config
import pymongo
import time
import signal
import sys

# Import handlers
from Admins.stats import register_stats_handler
from Admins.premium import register_premium_commands
from XP_TOOLS.start import register_start_handler
from XP_TOOLS.ip_scanner import register_ip_scanner
from XP_TOOLS.inline_scanner import register_inline_scanner
from XP_TOOLS.account import register_account_handler
from XP_TOOLS.leaderboard import register_leaderboard_handler
from XP_TOOLS.contact import register_contactus_handler
from Admins.gift import register_gift_commands
from Admins.userinfo import register_userinfo_command
from Admins.broadcast import register_broadcast_command
from Admins.user_management import register_user_management_commands
from Admins.maintenance import register_maintenance_commands
from XP_TOOLS.policy import register_policy_handler
from Admins.admin_help import register_admin_help_handler
from force_join import register_force_join_handlers, is_user_member, ask_user_to_join

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB setup
try:
    mongo_client = pymongo.MongoClient(config.con.MONGO_URI)
    db = mongo_client[config.con.MONGO_DB]
    users_collection = db[config.con.USERS_COLLECTION]
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise e

# Initialize bot
app = Client(
    "IP_BOT",
    api_id=config.con.API_ID,
    api_hash=config.con.API_HASH,
    bot_token=config.con.BOT_TOKEN
)

# ================== Register all handlers ================== #
register_force_join_handlers(app)  # Register force join handlers first

# Modify start handler to check for membership
register_start_handler(app, db, users_collection, is_user_member, ask_user_to_join)

# Modify other handlers to check for membership
register_account_handler(app, db)
register_ip_scanner(app, db, is_user_member, ask_user_to_join)
register_inline_scanner(app, db, is_user_member, ask_user_to_join)
register_leaderboard_handler(app, db) 
register_contactus_handler(app)

# Admin handlers don't need force join check
register_stats_handler(app)
register_premium_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
register_gift_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
register_userinfo_command(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
register_broadcast_command(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
register_user_management_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
register_maintenance_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
register_policy_handler(app)
register_admin_help_handler(app)

# Signal handler for graceful shutdown
def signal_handler(signum, frame):
    logger.info("Received shutdown signal. Stopping bot...")
    app.stop()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ================== Run Bot ================== #
if __name__ == "__main__":
    logger.info("Starting bot in polling mode...")
    
    try:
        # Start the bot
        app.run()
        
        # Keep the bot running
        logger.info("Bot is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(3600)  # Sleep for 1 hour
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed with error: {e}")
    finally:
        app.stop()
        logger.info("Bot stopped successfully")

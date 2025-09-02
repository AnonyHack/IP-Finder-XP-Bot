# main.py
import logging
import os
import asyncio
import sys
from flask import Flask, request, jsonify
from pyrogram import Client

# Load configuration from environment variables
class Config:
    def __init__(self):
        self.API_ID = int(os.getenv("API_ID", "25753873"))
        self.API_HASH = os.getenv("API_HASH", "3a5cdc2079cd76af80586102bd9761e2")
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "8243504414:AAGdCRSYTg_nG-ZQq02voxj3mrxXNadwtXQ")
        self.IP_API = os.getenv("ACCESS_TOKEN", "2bf134b73f3948")
        self.MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://anonymousguywas:12345Trials@cluster0.t4nmrtp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.MONGO_DB = os.getenv("MONGO_DB", "ipfinderbot")
        self.USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
        self.ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "5962658076").split(",")]
        self.BOT_URL = os.getenv("BOT_URL", "https://t.me/IpTrackerxpbot")
        self.SCANS_LIMIT = 5
        self.PREMIUM_SCANS = 50
        
        self.REQUIRED_CHANNELS = [
            {"label": "📢 Main Channel", "url": "https://t.me/Megahubbots", "chat": "@Megahubbots"},
        ]

# Create config instance
con = Config()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import handlers
try:
    import pymongo
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
except ImportError as e:
    logging.error(f"Import error: {e}")
    raise

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB setup
try:
    mongo_client = pymongo.MongoClient(con.MONGO_URI)
    db = mongo_client[con.MONGO_DB]
    users_collection = db[con.USERS_COLLECTION]
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise e

# Initialize bot
app = Client(
    "IP_BOT",
    api_id=con.API_ID,
    api_hash=con.API_HASH,
    bot_token=con.BOT_TOKEN
)

# Flask app for webhook
flask_app = Flask(__name__)

@flask_app.route(f'/{con.BOT_TOKEN}', methods=['POST'])
def handle_webhook():
    try:
        data = request.get_json()
        # Process update asynchronously
        asyncio.create_task(app.process_update(data))
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@flask_app.route('/')
def health_check():
    return 'OK'

def register_all_handlers():
    """Register all bot handlers"""
    register_force_join_handlers(app)
    register_start_handler(app, db, users_collection, is_user_member, ask_user_to_join)
    register_account_handler(app, db)
    register_ip_scanner(app, db, is_user_member, ask_user_to_join)
    register_inline_scanner(app, db, is_user_member, ask_user_to_join)
    register_leaderboard_handler(app, db)
    register_contactus_handler(app)

    # Admin handlers
    register_stats_handler(app)
    register_premium_commands(app, db, ADMIN_IDS=con.ADMIN_USER_IDS)
    register_gift_commands(app, db, ADMIN_IDS=con.ADMIN_USER_IDS)
    register_userinfo_command(app, db, ADMIN_IDS=con.ADMIN_USER_IDS)
    register_broadcast_command(app, db, ADMIN_IDS=con.ADMIN_USER_IDS)
    register_user_management_commands(app, db, ADMIN_IDS=con.ADMIN_USER_IDS)
    register_maintenance_commands(app, db, ADMIN_IDS=con.ADMIN_USER_IDS)
    register_policy_handler(app)
    register_admin_help_handler(app)

async def main():
    # Register all handlers
    register_all_handlers()
    
    # Start the client
    await app.start()
    logger.info("Bot client started successfully")
    
    # Check if we're on Render
    is_render = bool(os.environ.get('RENDER', False))
    
    if is_render:
        logger.info("🌐 Running in Webhook mode on Render...")
        
        # Get Render's external hostname
        webhook_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
        webhook_url = f"https://{webhook_host}/{con.BOT_TOKEN}"
        port = int(os.environ.get("PORT", 1000))
        
        try:
            await app.set_webhook(
                url=webhook_url,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            logger.info(f"Webhook set to: {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            await app.stop()
            return

        
        # Start Flask server
        from waitress import serve
        logger.info(f"Starting Flask server on port {port}")
        serve(flask_app, host="0.0.0.0", port=port)
        
    else:
        logger.info("🤖 Running in Polling mode locally...")
        # For local development, keep running
        await asyncio.Event().wait()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

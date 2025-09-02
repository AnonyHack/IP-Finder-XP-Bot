# main.py
from pyrogram import Client
import logging
import config
import pymongo
import os
import asyncio
from aiohttp import web

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

# Webhook configuration for Render
WEBHOOK_PATH = f"/{config.con.BOT_TOKEN}"
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'https://ip-finder-xp-bot.onrender.com')}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 1000))

# Webhook handlers
async def handle_webhook(request):
    """Handle incoming webhook updates"""
    try:
        data = await request.json()
        await app.process_update(data)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(status=500)

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="OK")

# ================== Register all handlers ================== #
def register_handlers():
    register_force_join_handlers(app)
    register_start_handler(app, db, users_collection, is_user_member, ask_user_to_join)
    register_account_handler(app, db)
    register_ip_scanner(app, db, is_user_member, ask_user_to_join)
    register_inline_scanner(app, db, is_user_member, ask_user_to_join)
    register_leaderboard_handler(app, db) 
    register_contactus_handler(app)

    # Admin handlers
    register_stats_handler(app)
    register_premium_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
    register_gift_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
    register_userinfo_command(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
    register_broadcast_command(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
    register_user_management_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
    register_maintenance_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
    register_policy_handler(app)
    register_admin_help_handler(app)

async def main():
    # Register all handlers
    register_handlers()
    
    # Start the client
    await app.start()
    logger.info("Bot started successfully")
    
    # Check if we're on Render (webhook mode)
    if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
        logger.info("🌐 Running in Webhook mode on Render...")
        
        # Set webhook
        try:
            await app.bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            logger.info(f"Webhook set to: {WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            await app.stop()
            return
        
        # Start web server
        server = web.Application()
        server.router.add_post(WEBHOOK_PATH, handle_webhook)
        server.router.add_get("/", health_check)
        
        runner = web.AppRunner(server)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        
        logger.info(f"Web server started on port {PORT}")
        
        # Keep the server running
        await asyncio.Event().wait()
        
    else:
        logger.info("🤖 Running in Polling mode locally...")
        # For local development, use idle
        await app.idle()

# ================== Run Bot ================== #
if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

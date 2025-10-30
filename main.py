# main.py
from pyrogram import Client
import logging, sys, traceback
import config
import pymongo
import time
import threading
import requests
from flask import Flask, jsonify
import os
import asyncio
from logging.handlers import RotatingFileHandler

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

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File handler with rotation
file_handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(log_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Get logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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
def register_handlers():
    try:
        print("🔄 Registering force join handlers...")
        register_force_join_handlers(app)
        
        print("🔄 Registering start handler...")
        register_start_handler(app, db, users_collection, is_user_member, ask_user_to_join)
        
        print("🔄 Registering account handler...")
        register_account_handler(app, db)
        
        print("🔄 Registering IP scanner...")
        register_ip_scanner(app, db, is_user_member, ask_user_to_join)
        
        print("🔄 Registering inline scanner...")
        register_inline_scanner(app, db, is_user_member, ask_user_to_join)
        
        print("🔄 Registering leaderboard...")
        register_leaderboard_handler(app, db)
        
        print("🔄 Registering contact...")
        register_contactus_handler(app)

        # Admin handlers
        print("🔄 Registering stats...")
        register_stats_handler(app)
        
        print("🔄 Registering premium commands...")
        register_premium_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
        
        print("🔄 Registering gift commands...")
        register_gift_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
        
        print("🔄 Registering userinfo...")
        register_userinfo_command(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
        
        print("🔄 Registering broadcast...")
        register_broadcast_command(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
        
        print("🔄 Registering user management...")
        register_user_management_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
        
        print("🔄 Registering maintenance...")
        register_maintenance_commands(app, db, ADMIN_IDS=config.con.ADMIN_USER_IDS)
        
        print("🔄 Registering policy...")
        register_policy_handler(app)
        
        print("🔄 Registering admin help...")
        register_admin_help_handler(app)

        print("✅ All handlers registered successfully!")
        
    except Exception as e:
        print(f"❌ Error registering handlers: {e}")
        traceback.print_exc()
        sys.exit(1)

# Import only the health server function, not the keep-alive with infinite loop
from keep_alive import run_health_server

if __name__ == '__main__':
    print("🚀 Starting IP Tracker Bot...")
    print(f"📱 API_ID: {config.con.API_ID}")
    print(f"🔑 BOT_TOKEN present: {bool(config.con.BOT_TOKEN)}")
    print(f"🗄️ MONGO_URI present: {bool(config.con.MONGO_URI)}")
    
    # Start health server in a separate thread (without the infinite ping loop)
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    print("✅ Health server started in separate thread")
    
    # Register handlers and start bot
    register_handlers()
    logger.info("Starting bot...")
    app.run()

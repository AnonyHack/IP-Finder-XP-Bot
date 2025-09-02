# config.py
from os import path, getenv

class config:
    API_ID = int(getenv("API_ID", "25753873"))
    API_HASH = getenv("API_HASH", "3a5cdc2079cd76af80586102bd9761e2")
    BOT_TOKEN = getenv("BOT_TOKEN", "8243504414:AAGdCRSYTg_nG-ZQq02voxj3mrxXNadwtXQ")
    IP_API = getenv("ACCESS_TOKEN", "2bf134b73f3948")
    MONGO_URI = getenv("MONGO_URI", "mongodb+srv://anonymousguywas:12345Trials@cluster0.t4nmrtp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    MONGO_DB = getenv("MONGO_DB", "ipfinderbot")
    USERS_COLLECTION = getenv("USERS_COLLECTION", "users")
    ADMIN_USER_IDS = [int(x) for x in getenv("ADMIN_USER_IDS", "5962658076").split(",")]
    BOT_URL = getenv("BOT_URL", "https://t.me/IpTrackerxpbot")  # change this anytime
    SCANS_LIMIT = 5  # free daily scans, can change later
    PREMIUM_SCANS = 50  # premium daily scans, can change later
    
    # Add required channels for force join
    REQUIRED_CHANNELS = [
        {"label": "📢 Main Channel", "url": "https://t.me/Megahubbots", "chat": "@Megahubbots"},
        #{"label": "🗣 Discussion Group", "url": "https://t.me/your_discussion_group", "chat": "@your_discussion_group"}
    ]
    
    # Webhook Configuration
    WEBHOOK_HOST = getenv("WEBHOOK_HOST", "")  # Will be set automatically on Render
    WEBHOOK_PATH = f"/{BOT_TOKEN}"  # Webhook path
    WEBHOOK_URL = f"https://{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else ""
    PORT = int(getenv("PORT", 1000))  # Port for web server
    WEBHOOK_SECRET = getenv("WEBHOOK_SECRET", "12345")  # Optional security


con = config()
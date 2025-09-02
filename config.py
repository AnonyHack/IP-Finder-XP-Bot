# config.py
import os

class config:
    API_ID = int(os.getenv("API_ID", "25753873"))
    API_HASH = os.getenv("API_HASH", "3a5cdc2079cd76af80586102bd9761e2")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8243504414:AAGdCRSYTg_nG-ZQq02voxj3mrxXNadwtXQ")
    IP_API = os.getenv("ACCESS_TOKEN", "2bf134b73f3948")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://anonymousguywas:12345Trials@cluster0.t4nmrtp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    MONGO_DB = os.getenv("MONGO_DB", "ipfinderbot")
    USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
    ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "5962658076").split(",")]
    BOT_URL = os.getenv("BOT_URL", "https://t.me/IpTrackerxpbot")
    SCANS_LIMIT = 5
    PREMIUM_SCANS = 50
    
    REQUIRED_CHANNELS = [
        {"label": "📢 Main Channel", "url": "https://t.me/Megahubbots", "chat": "@Megahubbots"},
    ]

con = config()

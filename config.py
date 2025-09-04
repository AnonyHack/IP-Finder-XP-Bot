# config.py
from os import path, getenv

class config:
    API_ID = int(getenv("API_ID", ""))
    API_HASH = getenv("API_HASH", "")
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    IP_API = getenv("ACCESS_TOKEN", "")  # get your free token from ipgeolocation.io
    MONGO_URI = getenv("MONGO_URI", "")
    MONGO_DB = getenv("MONGO_DB", "ipfinderbot")
    USERS_COLLECTION = getenv("USERS_COLLECTION", "users")
    ADMIN_USER_IDS = [int(x) for x in getenv("ADMIN_USER_IDS", "").split(",")]
    BOT_URL = getenv("BOT_URL", "https://t.me/IpTrackerxpbot")  # change this anytime
    SCANS_LIMIT = 5  # free daily scans, can change later
    PREMIUM_SCANS = 50  # premium daily scans, can change later
        # Media & Links
    START_PHOTO_URL = getenv("START_PHOTO_URL", "https://i.ibb.co/C5x5KCdn/LG.jpg")
    BOT_GUIDE_VIDEO_URL = getenv("BOT_GUIDE_VIDEO_URL", "https://youtube.com/your-tutorial-link")
    BOT_DEVELOPER = getenv("BOT_DEVELOPER", "https://t.me/Am_ItachiUchiha")
    POWERED_BY = getenv("POWERED_BY", "https://t.me/Megahubbots")



    
    # Add required channels for force join
    REQUIRED_CHANNELS = [
        {"label": "📢 Bot Updates", "url": "https://t.me/Megahubbots", "chat": "@Megahubbots"},
        {"label": "📢 Promoter Channel", "url": "https://t.me/Freenethubz", "chat": "@Freenethubz"}
    ]


con = config()

# config.py
from os import getenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class config:
    # --- API_ID: int, works with or without quotes ---
    _api_id = getenv("API_ID", "").strip().strip('"')
    API_ID = int(_api_id) if _api_id and _api_id.isdigit() else 0

    API_HASH = getenv("API_HASH", "")
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    IP_API = getenv("ACCESS_TOKEN", "") # get your free token from ipgeolocation.io
    MONGO_URI = getenv("MONGO_URI", "")
    MONGO_DB = getenv("MONGO_DB", "ipfindertest")
    USERS_COLLECTION = getenv("USERS_COLLECTION", "users")

    # --- ADMIN_USER_IDS: list of ints, works with or without quotes, ignores spaces ---
    _admin_raw = getenv("ADMIN_USER_IDS", "").strip().strip('"')
    ADMIN_USER_IDS = []
    if _admin_raw:
        parts = [x.strip() for x in _admin_raw.split(",") if x.strip()]
        try:
            ADMIN_USER_IDS = [int(x) for x in parts]
        except ValueError:
            ADMIN_USER_IDS = []  # fallback if any invalid
    
    BOT_URL = getenv("BOT_URL", "https://t.me/IpTrackertestbot")
    SCANS_LIMIT = 5  # free daily scans, can change later
    PREMIUM_SCANS = 50  # premium daily scans, can change later

    # Media & Links
    START_PHOTO_URL = getenv("START_PHOTO_URL", "https://i.ibb.co/BXSX8N0/iplogo.jpg")
    BOT_GUIDE_VIDEO_URL = getenv("BOT_GUIDE_VIDEO_URL", "https://youtube.com/@FREENETHUBTECH")
    BOT_DEVELOPER = getenv("BOT_DEVELOPER", "https://t.me/Am_ItachiUchiha")
    POWERED_BY = getenv("POWERED_BY", "https://t.me/XPTOOLSTEAM")
    NOTIFICATION_CHANNEL = getenv("NOTIFICATION_CHANNEL", "@XPTOOLSLOGS")

    # Add required channels for force join
    REQUIRED_CHANNELS = [
        {"label": "📢 Bot Updates", "url": "https://t.me/XPTOOLSTEAM", "chat": "@XPTOOLSTEAM"},
       # {"label": "📢 Promoter Channel", "url": "https://t.me/Freenethubz", "chat": "@Freenethubz"}
    ]

    # Add validation for required credentials
    def validate_credentials(self):
        if not self.API_ID:
            raise ValueError("API_ID is required but not found in .env file")
        if not self.API_HASH:
            raise ValueError("API_HASH is required but not found in .env file")
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required but not found in .env file")
        if not self.IP_API:
            raise ValueError("IP_API is required but not found in .env file")

# --- Application PORT ---
PORT = 10000

con = config()

# Validate that required credentials are present
con.validate_credentials()

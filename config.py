from loguru import logger
from pyrogram import enums
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "tiktok_downloader"

ADMINS = [5962658076]

NOTIFICATION_CHANNEL = os.getenv("NOTIFICATION_CHANNEL", "@XPTOOLSLOGS")  # Replace with your actual channel Name

# Keep Alive Server Port
PORT = int(os.getenv("PORT", 10000))  # Default to 8080 if not set

# Bot Information
BOT_NAME = "TikTok Downloader"
BOT_USERNAME = "tiktokdownloaderxpbot"  # Without @
OWNER_USERNAME = "Am_itachiuchiha"     # Without @

# Website URL
WEBSITE_URL = "https://tiktokdownloaderxp.onrender.com/"

# Links
START_PHOTO_URL = "https://i.ibb.co/BXSX8N0/iplogo.jpg"
SOURCE_CODE_URL = "https://t.me/Am_itachiuchiha"
SUPPORT_GROUP_URL = "https://t.me/Free_Vpn_Chats"
YOUTUBE_TUTORIAL_URL = "https://youtube.com/@freenethubtech"

# About Page
ABOUT_PAGE = f"""
<b> ⍟───[ ᴍʏ ᴅᴇᴛᴀɪʟꜱ ]───⍟ </b>

<blockquote>
‣ ᴍʏ ɴᴀᴍᴇ : <a href="https://t.me/{BOT_USERNAME}">{BOT_NAME}</a> 🔍
‣ ᴍʏ ʙᴇsᴛ ғʀɪᴇɴᴅ : <a href="tg://settings">ᴛʜɪs ᴘᴇʀsᴏɴ</a>
‣ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href="https://t.me/{OWNER_USERNAME}">ɪᴛᴀᴄʜɪ ᴜᴄʜɪʜᴀ</a>
‣ ʟɪʙʀᴀʀʏ : <a href="https://docs.pyrogram.org/">ᴘʏʀᴏɢʀᴀᴍ</a>
‣ ʟᴀɴɢᴜᴀɢᴇ : <a href="https://www.python.org/download/releases/3.0/">ᴘʏᴛʜᴏɴ 3</a>
‣ ᴅᴀᴛᴀ ʙᴀsᴇ : <a href="https://www.mongodb.com/">ᴍᴏɴɢᴏ ᴅʙ</a>
‣ ʙᴏᴛ sᴇʀᴠᴇʀ : <a href="https://heroku.com/">ʜᴇʀᴏᴋᴜ</a>
‣ ʙᴜɪʟᴅ sᴛᴀᴛᴜs : <a href="#">ᴠ1.0 [sᴛᴀʙʟᴇ]</a>
</blockquote>
"""

# Tutorial Page
TUTORIAL_PAGE = """
<blockquote><b> ⍟───[ ʜᴏᴡ ᴛᴏ ᴜsᴇ ]───⍟ </b></blockquote>

<blockquote>
1. <b>Get TikTok Video URL</b>
   - Open TikTok app
   - Find the video you want to download
   - Tap on "Share" button
   - Copy the link

2. <b>Use Our Website</b>
   - Visit our downloader website
   - Paste the TikTok URL
   - Click "Download Video"
   - Wait for processing
   - Download your video without watermark!

3. <b>Features</b>
   - No watermark
   - High quality
   - Fast processing
   - Free to use
</blockquote>

<b>Need visual guidance? Watch our tutorial video!</b>
"""

# Parse Mode
PARSE_MODE = enums.ParseMode.HTML

# Logging configuration
logger.add("bot.log", rotation="10 MB", retention="10 days", level="INFO")
logger.info("✅ Bot configuration loaded successfully")

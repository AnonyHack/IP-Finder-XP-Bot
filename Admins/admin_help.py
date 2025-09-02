from pyrogram import Client, filters
from config import con  # import the config instance
ADMIN_USER_IDS = con.ADMIN_USER_IDS

# Expose command metadata
COMMANDS = [("admin_help", " 🛂 Admin Panel Dashboard")]

# Define admin commands list
ADMIN_COMMANDS = """
👑 <b>Admin Commands</b> 👑

/stats - 📈 Check Bot Statistics
/userinf - 📇 Check Users Info
/giftc - 🧧 Generate Gift Codes
/giftcodes - 🧧 Check Gift Codes Status
/addprem - 💎 Add User To Premium
/removeprem - 💎 Remove User To Premium
/ban - 👮‍♂️ Ban User
/unban - 👮‍♂️ Unban User
/bannedlist - 🧾 Check Banned Users
/deleteuser - 🗑️ Delete User From Database
/broadcast - 📤 Broadcast Message
/pinm - 📌 Pinned Broadcast
/bcmedia - 📰 Media Broadcast
/pinmedia - 📍 Pinned Media Broadcast
/mainmode - 🖲️ Turn On Maintenance Mode
/mainstatus - 🖲️ Check Maintenance Status

"""

def register_admin_help_handler(app: Client):
    @app.on_message(filters.command("adminhelp"))
    async def admin_help(client, message):
        if message.from_user.id not in ADMIN_USER_IDS:
            return await message.reply_text("🚫 You don’t have permission to use this command.")
        
        await message.reply_text(
            ADMIN_COMMANDS,
            quote=True,
            parse_mode="html"
        )

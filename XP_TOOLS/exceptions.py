# XP_TOOLS/exceptions.py

# ✅ Commands that should never be blocked by the "ignore commands" logic
ALLOWED_COMMANDS = [
    "/start",
    "/help",
    "/stats",
    "/about",
    "/myaccount",   # include /myaccount too
    "/addprem",      # admin command, useful to keep
    "/removeprem"    # admin command, useful to keep
]

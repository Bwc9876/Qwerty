import os

from dotenv import load_dotenv

load_dotenv(".env")

DEBUG = True
KEY = os.getenv("BOT_KEY", None)

if DEBUG:
    DEBUG_GUILDS = [int(guild_id) for guild_id in os.getenv("DEBUG_GUILDS", "").split(",")]
else:
    DEBUG_GUILDS = []

AVAILABLE_COGS = {
    'bot_base.cogs': ('BaseBot',),
}

import os

from dotenv import load_dotenv

load_dotenv(".env")

KEY = os.getenv("BOT_KEY", None)

AVAILABLE_COGS = {
    'bot_base.cogs': ('BaseBot',),
}

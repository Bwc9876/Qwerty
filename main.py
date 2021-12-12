import importlib
import inspect
import os
from time import sleep

import discord
import django
from discord.ext import commands

import bot_settings


def load_msg(msg: str):
    print(" " * 100, end="\r")
    print("\033[33m" + "⌛" + "\033[m" + f" Loading: {msg}", end="\r")
    sleep(0.2)


load_msg("Starting Django (Stage 1/4)")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_settings')
django.setup()

load_msg("Instantiating Bot (Stage 2/4)")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents)


@bot.event
async def on_ready():
    print("", end="\r")
    print("\033[32m" + "✔" + "\033[m" + f" {bot.user.display_name} Online With The Following Cogs:")
    print('\n'.join([f'• {str(cog)}' for cog in bot.cogs]))
    print("Press ^C To Exit")


for index, module_path in enumerate(bot_settings.AVAILABLE_COGS.keys()):
    cogs = bot_settings.AVAILABLE_COGS[module_path]
    load_msg("Loading Cogs: " + ', '.join([f"{module_path}.{cog_name}" for cog_name in cogs]) + f" (Module {index + 1}/{len(bot_settings.AVAILABLE_COGS.keys())}) (Stage 3/4)")
    module = importlib.import_module(module_path)
    classes = {k: v for k, v in inspect.getmembers(module, inspect.isclass)}
    for raw_cog in cogs:
        if raw_cog in classes.keys():
            cog = classes.get(raw_cog)(bot)
            if issubclass(cog.__class__, commands.Cog):
                bot.add_cog(cog)
            else:
                raise TypeError(f"Class '{raw_cog}' is not a Cog")
        else:
            raise ImportError(f"Can't find cog class: '{raw_cog}'")

load_msg("Starting Bot (Stage 4/4)")

if bot_settings.KEY is not None:
    bot.run(bot_settings.KEY)
else:
    raise TypeError("The bot key cannot be None!")

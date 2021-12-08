import os
import importlib
import inspect

import django
import discord
from discord.commands import slash_command
from discord.ext import commands

import bot_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_settings')
django.setup()

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="~", intents=intents)

for module_path in bot_settings.AVAILABLE_COGS.keys():
    cogs = bot_settings.AVAILABLE_COGS[module_path]
    module = importlib.import_module(module_path)
    classes = {k: v for k, v in inspect.getmembers(module, inspect.isclass)}
    for raw_cog in cogs:
        if raw_cog in classes.keys():
            cog = classes.get(raw_cog)
            if issubclass(cog, commands.Cog):
                bot.add_cog(cog(bot))
            else:
                raise TypeError(f"Class '{raw_cog}' is not a Cog")
        else:
            raise ImportError(f"Can't find cog class: '{raw_cog}'")

if bot_settings.KEY is not None:
    bot.run(bot_settings.KEY)
else:
    raise TypeError("The bot key cannot be None!")

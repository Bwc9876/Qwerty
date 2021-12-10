import os
import importlib
import inspect

import django
import discord
from discord.ext import commands

import bot_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_settings')
django.setup()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(intents=intents)

if bot_settings.DEBUG:
    print("Debugging Is On With The Following Guilds:")
    print('\n'.join([f"- {str(guild_id)}" for guild_id in bot_settings.DEBUG_GUILDS]))

@bot.event
async def on_ready():
    print("Bot Online With The Following Cogs:")
    print('\n'.join([f'- {str(cog)}' for cog in bot.cogs]))

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

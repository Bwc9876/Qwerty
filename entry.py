import os
import importlib
import inspect

import django
import discord
from discord.ext import commands

import bot_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_settings')
django.setup()


async def determine_prefix(in_bot: commands.Bot, ctx: commands.Context) -> str:
    if ctx.guild is None:
        return "~"
    else:
        from persistence import get_or_create_server_data
        server_data = await get_or_create_server_data(ctx.guild.id)
        return server_data.prefix


bot = commands.Bot(command_prefix=determine_prefix)


@bot.event
async def on_ready():
    print("--Bot Started--")
    activity = discord.Game(name='~help', type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Invalid command, use {await bot.command_prefix(bot, ctx)}help for help")
    else:
        raise error

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

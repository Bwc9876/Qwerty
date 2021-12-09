from discord.commands import slash_command, application_command, SlashCommand, CheckFailure
from discord.ext import commands

import bot_settings
from bot_settings import DEBUG_GUILDS
from .exceptions import ImproperlyConfiguredCogError, NoCogDataError
from .models import BaseCogData
import persistence


class BaseCog(commands.Cog):

    cog_data_model = None

    def inject_checks(self):
        for command in self.__cog_commands__:
            command.checks.append(self.cog_check)

    def __init__(self, bot: commands.Bot):
        if self.cog_data_model is not None and issubclass(self.cog_data_model, BaseCogData) is False:
            raise ImproperlyConfiguredCogError(f"cog_data_model must of of type 'BaseCogData', not '{type(self.cog_data_model)}'")
        self.bot = bot
        self.inject_checks()

    async def load_data(self, server_id: int):
        if self.cog_data_model is None:
            raise NoCogDataError("This cog doesn't have a model defined!")
        else:
            return await persistence.get_or_create_cog_data(self.cog_data_model, server_id)

    async def save_data(self, data):
        await persistence.save_cog_data(data)

    async def cog_data_check(self, ctx, data):
        return True

    async def cog_check(self, ctx):
        if ctx.guild is None:
            await ctx.respond("This command can only be used in a server")
            return False
        else:
            data = await self.load_data(ctx.guild.id)
            if data.enabled:
                return await self.cog_data_check(ctx, data)
            else:
                await ctx.respond("This command is disabled")
                return False

    async def cog_command_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            pass
        else:
            raise error


class BaseBot(commands.Cog, name="Basic Commands"):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="blip", description="Responds with 'blop'", guild_ids=DEBUG_GUILDS)
    async def blip(self, ctx):
        await ctx.respond("blop")

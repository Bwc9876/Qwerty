from discord.ext import commands

from .exceptions import ImproperlyConfiguredCogError, NoCogDataError
from .models import BaseCogData
import persistence


class BaseCog(commands.Cog):

    cog_data_model = None

    def __init__(self, bot: commands.Bot):
        if self.cog_data_model is not None and issubclass(self.cog_data_model, BaseCogData) is False:
            raise ImproperlyConfiguredCogError(f"cog_data_model must of of type 'BaseCogData', not '{type(self.cog_data_model)}'")
        self.bot = bot

    async def load_data(self, server_id: int):
        if self.cog_data_model is None:
            raise NoCogDataError("This cog doesn't have a model defined!")
        else:
            return await persistence.get_or_create_cog_data(self.cog_data_model, server_id)

    async def save_data(self, data):
        await persistence.save_cog_data(data)

    async def cog_check(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server")
            return False
        else:
            data = await self.load_data(ctx.guild.id)
            if data.enabled:
                return True
            else:
                await ctx.send("This command is disabled")
                return False

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.CheckFailure):
            pass
        else:
            raise error


class BaseBot(commands.Cog, name="Basic Commands"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="blip", description="Responds with 'blop'", brief="Test the bot")
    async def blip(self, ctx):
        await ctx.send("blop")

    @commands.command(name="set-prefix", description="Set the prefix of this server", brief="Change the prefix")
    async def set_prefix(self, ctx: commands.Context, *, prefix: str):
        if ctx.guild is None:
            await ctx.send('You can only use that command in a server')
        else:
            if len(prefix) != 1:
                await ctx.send('Prefix must be one character')
            else:
                server_data = await persistence.get_or_create_server_data(ctx.guild.id)
                server_data.prefix = prefix
                await persistence.save_server_data(server_data)
                await ctx.send(f'Prefix is now: \"{prefix}\"')

    @set_prefix.error
    async def _prefix_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Please enter a prefix")
        else:
            raise error

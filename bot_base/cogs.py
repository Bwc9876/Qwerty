from discord.commands import slash_command, CheckFailure, Option, AutocompleteContext, ApplicationContext, permissions
from discord.ext import commands
from discord.utils import basic_autocomplete

import persistence
from bot_settings import DEBUG_GUILDS
from .exceptions import ImproperlyConfiguredCogError, NoCogDataError
from .models import BaseCogData


async def cog_autocomplete(ctx: AutocompleteContext):
    return list(ctx.bot.cogs.keys())


class BaseCog(commands.Cog):
    cog_data_model = None

    def inject_checks(self):
        for command in self.__cog_commands__:
            command.checks.append(self.cog_check)

    def __init__(self, bot: commands.Bot):
        if self.cog_data_model is not None and issubclass(self.cog_data_model, BaseCogData) is False:
            raise ImproperlyConfiguredCogError(
                f"cog_data_model must of of type 'BaseCogData', not '{type(self.cog_data_model)}'")
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

    async def cog_check(self, ctx: ApplicationContext):
        if ctx.guild is None:
            await ctx.respond("This command can only be used in a server", ephemeral=True)
            return False
        else:
            data = await self.load_data(ctx.guild.id)
            if data.enabled:
                return await self.cog_data_check(ctx, data)
            else:
                await ctx.respond("This command is disabled", ephemeral=True)
                return False

    async def cog_command_error(self, ctx: ApplicationContext, error):
        if isinstance(error, CheckFailure):
            pass
        else:
            raise error


class BaseBot(commands.Cog, name="Base Bot"):

    def __init__(self, bot):
        self.bot = bot

    async def enable_or_disable_cog(self, cog_name, server_id, enabled):
        try:
            cog = self.bot.cogs[cog_name]
            if issubclass(cog.__class__, BaseCog) and hasattr(cog, 'cog_data_model') and cog.cog_data_model is not None:
                cog_data = await cog.load_data(server_id)
                cog_data.enabled = enabled
                await cog.save_data(cog_data)
            else:
                raise ValueError("That Cog Cannot Be Changed")
        except KeyError:
            raise ValueError(f"There Is No Cog Named: {cog_name}")

    @slash_command(name="blip", description="Responds with 'blop'", guild_ids=DEBUG_GUILDS)
    async def blip(self, ctx: ApplicationContext):
        await ctx.respond("blop")

    @slash_command(name="enable-cog", description="Enable A Cog For This Server", guild_ids=DEBUG_GUILDS)
    @permissions.is_owner()
    async def enable(self, ctx: ApplicationContext, cog_name: Option(str, description="The name of the cog to enable",
                                                                     autocomplete=basic_autocomplete(
                                                                         cog_autocomplete))):
        try:
            await self.enable_or_disable_cog(cog_name, ctx.interaction.guild.id, enabled=True)
            await ctx.respond("Cog Enabled", ephemeral=True)
        except ValueError as error:
            await ctx.respond(error.args[0], ephemeral=True)

    @slash_command(name="disable-cog", description="Disable A Cog For This Server", guild_ids=DEBUG_GUILDS)
    @permissions.is_owner()
    async def disable(self, ctx: ApplicationContext, cog_name: Option(str, description="The name of the cog to disable",
                                                                      autocomplete=basic_autocomplete(
                                                                          cog_autocomplete))):
        try:
            await self.enable_or_disable_cog(cog_name, ctx.interaction.guild.id, enabled=False)
            await ctx.respond("Cog Disabled", ephemeral=True)
        except ValueError as error:
            await ctx.respond(error.args[0], ephemeral=True)

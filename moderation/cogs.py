from datetime import datetime, timedelta

from discord.commands import slash_command, ApplicationContext, Option
from discord.member import Member

from bot_base.cogs import BaseCog
from bot_settings import DEBUG_GUILDS
from persistence import _, queryset_to_list
from .models import ModerationCogData, ModWarning


class Moderation(BaseCog, name="Moderation"):
    cog_data_model = ModerationCogData

    COMMAND_PERMS = (
        ('warn', 'kick', 'forgive'),
        ('ban', 'unban')
    )

    async def cog_data_check(self, ctx: ApplicationContext, data: ModerationCogData):
        cmd_name = ctx.command.qualified_name()
        if cmd_name in self.COMMAND_PERMS[0]:
            if ctx.interaction.user.guild_permissions.administrator or data.moderator_role_id is not None and (
                    ctx.interaction.user.get_role(data.moderator_role_id) is not None or ctx.interaction.user.get_role(
                    data.administrator_role_id) is not None):
                return True
            else:
                await ctx.respond("You lack permissions to perform this command", ephemeral=True)
                return False
        elif cmd_name in self.COMMAND_PERMS[1]:
            if data.administrator_role_id is not None and ctx.interaction.user.get_role(
                    data.administrator_role_id) is not None:
                return True
            else:
                await ctx.respond("You lack permissions to perform this command", ephemeral=True)
                return False
        else:
            return True

    async def load_warnings(self, data: ModerationCogData, user_id: int):
        warnings: list[ModWarning] = await _(queryset_to_list)(await _(data.warnings.filter)(user_id=user_id))
        for warning in warnings:
            if datetime.now().date() >= (warning.date_created + warning.forget_time):
                await _(warning.delete)()
                warnings.remove(warning)
        return warnings

    async def check_supersedes(self, data: ModerationCogData, invoker: Member, target: Member, guild):
        if target.id == guild.owner_id:
            return False
        elif invoker.id == guild.owner_id:
            return True
        elif (invoker.get_role(data.moderator_role_id) is not None) and (target.get_role(data.administrator_role_id) is not None):
            return False
        elif (invoker.get_role(data.moderator_role_id) is not None) and (target.get_role(data.moderator_role_id) is not None):
            return False
        else:
            return True

    @slash_command(name="warnings", description="Get the warnings for yourself or another user", guild_ids=DEBUG_GUILDS)
    async def list_warnings(self, ctx: ApplicationContext,
                            user: Option(Member, "Pick a user to show the warnings for [Optional]", required=False,
                                         default=None)):
        if user is None:
            user = ctx.interaction.user
        data = await self.load_data(ctx.guild.id)
        warnings = await self.load_warnings(data, user.id)
        response_str = f"{user.mention} Has {len(warnings)} Warnings"
        for warning in warnings:
            reason_str = "No Reason Provided" if warning.reason is None else warning.reason
            reporter = ctx.interaction.guild.get_member(warning.reporter_id)
            reporter_str = "<Left Server>" if reporter is None else reporter.name
            response_str += f"\n```\n==On {warning.date_created}==\nReason: {reason_str}\nReporter: {reporter_str}\n```"
        await ctx.respond(response_str)

    @slash_command(name="warn", description="Create a warning for a specific user", guild_ids=DEBUG_GUILDS)
    async def warn(self, ctx: ApplicationContext, user: Option(Member, "The user to warn"),
                   reason: Option(str, "Enter the reason for the warning [Optional]", required=False, default=None),
                   days: Option(int, "Enter the days the warning lasts for [Optional]", required=False, default=7)):
        data: ModerationCogData = await self.load_data(ctx.guild.id)
        if await self.check_supersedes(data, ctx.interaction.user, user, ctx.interaction.guild):
            await _(ModWarning.objects.create)(parent_cog=data, user_id=user.id, reporter_id=ctx.interaction.user.id,
                                               reason=reason, forget_time=timedelta(days=days))
            warnings = await self.load_warnings(data, user.id)
            if len(warnings) == data.max_warnings_until_ban:
                await user.ban(reason="Exceeded Warning Limit")
                await ctx.respond(f"{user.name} Has Been Banned For Exceeding {data.max_warnings_until_ban} Warnings")
            else:
                reason_str = "" if reason is None else f"For: {reason}"
                await ctx.respond(f"{user.mention} You Have Received A Warning {reason_str}")
        else:
            await ctx.respond("You lack rank to perform that command", ephemeral=True)

    @slash_command(name="forgive", description="Clear all warnings for a user", guild_ids=DEBUG_GUILDS)
    async def forgive(self, ctx: ApplicationContext, user: Option(Member, "The user to forgive")):
        data: ModerationCogData = await self.load_data(ctx.interaction.guild.id)
        await _((await _(data.warnings.filter)(user_id=user.id)).delete)()
        await ctx.respond("User Forgiven", ephemeral=True)

    @slash_command(name="ban", description="Ban A User", guild_ids=DEBUG_GUILDS)
    async def ban(self, ctx: ApplicationContext, user: Option(Member, "The user to ban"),
                  reason: Option(str, "The reason why this user has been banned [Optional]", required=False,
                                 default="No Reason Provided")):
        data: ModerationCogData = await self.load_data(ctx.interaction.guild.id)
        if await self.check_supersedes(data, ctx.interaction.user, user, ctx.interaction.guild):
            await user.ban(reason=reason)
            await ctx.respond(f"{user.name} Has Been Banned For: {reason}")
        else:
            await ctx.respond("You lack rank to perform that command", ephemeral=True)

import os
from asyncio import create_subprocess_shell
from subprocess import PIPE

from discord.commands import slash_command, ApplicationContext, Option

from bot_settings import OWNER, DEBUG_GUILDS
from bot_base.cogs import BaseCog
from personal.models import PersonalCogData


class Personal(BaseCog, name="Personal"):

    cog_data_model = PersonalCogData

    def __init__(self, bot):
        super(Personal, self).__init__(bot)
        self.projector_proc = None

    async def cog_check(self, ctx: ApplicationContext):
        if ctx.interaction.user.id == OWNER:
            return True
        else:
            await ctx.respond("This command can only be invoked by the owner of this bot", ephemeral=True)
            return False

    @slash_command(name="projector", description="Start projector", guild_ids=DEBUG_GUILDS)
    async def projector(self, ctx: ApplicationContext, action: Option(str, description="The action to perform", choices=['start', 'stop'])):
        if action == 'start':
            if self.projector_proc is not None:
                await ctx.respond("Already Started")
            else:
                self.projector_proc = await create_subprocess_shell(os.getenv("PROJ_EXEC"), stdout=PIPE, cwd=os.getenv("PROJ_WORK_DIR"))
                await ctx.respond("Started")
        else:
            if self.projector_proc is not None:
                try:
                    self.projector_proc.kill()
                except ProcessLookupError:
                    pass
                self.projector_proc = None
                await ctx.respond("Stopped")
            else:
                await ctx.respond("Not Running (At Least in Subprocess)")




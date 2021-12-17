from datetime import datetime

from discord.commands import slash_command, ApplicationContext, AutocompleteContext, Option

from bot_base.cogs import BaseCog
from bot_settings import DEBUG_GUILDS
from dnd.models import DnDCogData, Campaign
from persistence import _

cmp_name = Option(str, name="Campaign Name", description="The name of the campaign")


class DnD(BaseCog, name='D&D'):

    cog_data_model = DnDCogData

    @staticmethod
    async def get_campaign(data: DnDCogData, dm_id, name):
        return await _(data.campaigns.get)(dungeon_master=dm_id, name=name, open=True)

    @slash_command(name='start-campaign', description='Start a Campaign', guild_ids=DEBUG_GUILDS)
    async def start_campaign(self, ctx: ApplicationContext, campaign_name: cmp_name):
        data: DnDCogData = await self.load_data(ctx.interaction.guild.id)
        if await _((await _(data.campaigns.filter)(dungeon_master=ctx.interaction.user.id)).count)() > 2:
            await ctx.respond("You can only have three campaigns in each server!", ephemeral=True)
        elif await _((await _(data.campaigns.filter)(name=campaign_name)).exists)():
            await ctx.respond("A campaign with that name already exists", ephemeral=True)
        else:
            new_campaign: Campaign = await _(data.campaigns.create)(name=campaign_name, dungeon_master=ctx.interaction.user.id)
            await _(new_campaign.players.create)(user_id=ctx.interaction.user.id)
            await ctx.respond(f"Campaign: `{campaign_name}` Has Been Created")

    @slash_command(name='close-campaign', description='temporarily closes a campaign', guild_ids=DEBUG_GUILDS)
    async def close_campaign(self, ctx: ApplicationContext, campaign_name: cmp_name):
        data: DnDCogData = await self.load_data(ctx.interaction.guild.id)
        try:
            target_campaign = await self.get_campaign(data, ctx.interaction.user.id, campaign_name)
            target_campaign.open = False
            target_campaign.date_closed = datetime.now()
            await _(target_campaign.save)()
            await ctx.respond("Campaign Closed")
        except Campaign.DoesNotExist:
            await ctx.respond("Campaign Not Found", ephemeral=True)


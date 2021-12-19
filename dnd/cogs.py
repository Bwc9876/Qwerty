from datetime import datetime
from math import floor

from discord import Embed
from discord.colour import Colour
from discord.commands import slash_command, ApplicationContext, AutocompleteContext, Option

from bot_base.cogs import BaseCog
from bot_settings import DEBUG_GUILDS
from dnd.models import DnDCogData, Campaign
from dnd.roller import parse_roll, RollingError
from persistence import _, queryset_to_list

new_cmp_name = Option(str, name="campaign-name", description="The name of the campaign")


async def campaign_autocomplete(ctx: AutocompleteContext):
    campaigns = await _(queryset_to_list)(
        await _(Campaign.objects.filter)(parent_cog__parent_server__pk=ctx.interaction.guild.id,
                                         dungeon_master=ctx.interaction.user.id))
    return [campaign.name for campaign in campaigns]


cmp_name = Option(str, name="campaign-name", description="The name of the campaign", autocomplete=campaign_autocomplete)


class DnD(BaseCog, name='D&D'):
    cog_data_model = DnDCogData

    @staticmethod
    async def get_campaign(data: DnDCogData, dm_id: int, name: str):
        return await _(data.campaigns.get)(dungeon_master=dm_id, name=name)

    @slash_command(name='start-campaign', description='Start a Campaign', guild_ids=DEBUG_GUILDS)
    async def start_campaign(self, ctx: ApplicationContext, campaign_name: new_cmp_name):
        data: DnDCogData = await self.load_data(ctx.interaction.guild.id)
        if await _(
                (await _(data.campaigns.filter)(dungeon_master=ctx.interaction.user.id, name=campaign_name)).exists)():
            await ctx.respond("A campaign with that name already exists", ephemeral=True)
        else:
            new_campaign: Campaign = await _(data.campaigns.create)(name=campaign_name,
                                                                    dungeon_master=ctx.interaction.user.id)
            await _(new_campaign.players.create)(user_id=ctx.interaction.user.id)
            await ctx.respond(f"Campaign: `{campaign_name}` Has Been Created")

    @slash_command(name='edit-campaign', description='temporarily closes a campaign', guild_ids=DEBUG_GUILDS)
    async def edit_campaign(self, ctx: ApplicationContext, campaign_name: cmp_name,
                            action: Option(str, choices=('open', 'close'))):
        data: DnDCogData = await self.load_data(ctx.interaction.guild.id)
        try:
            target_campaign = await self.get_campaign(data, ctx.interaction.user.id, campaign_name)
            target_campaign.open = action == 'close'
            if action == 'close':
                target_campaign.date_closed = datetime.now()
            await _(target_campaign.save)()
            await ctx.respond(f"Campaign {'Closed' if action == 'close' else 'Re-Opened'}")
        except Campaign.DoesNotExist:
            await ctx.respond("Campaign Not Found", ephemeral=True)

    @slash_command(name='my-campaigns', description='list your campaigns', guild_ids=DEBUG_GUILDS)
    async def list_campaigns(self, ctx: ApplicationContext):
        data: DnDCogData = await self.load_data(ctx.interaction.guild.id)
        campaigns: list[Campaign] = await _(queryset_to_list)(await _(data.campaigns.all)())
        output_message = 'Your Campaigns:\n```\n'
        for campaign in campaigns:
            output_message += campaign.name + ('' if campaign.open else ' (Closed)') + '\n'
        output_message += '```'
        await ctx.respond(output_message, ephemeral=True)

    ROLL_TYPES = {
        'advantage': 'A:',
        'disadvantage': 'D:',
        'flat': 'F:'
    }

    @slash_command(name='roll', description="perform a roll", guild_ids=DEBUG_GUILDS)
    async def roll(self, ctx: ApplicationContext, roll: Option(str, description="The roll to perform (ex: 1d20+1d6+5)"),
                   roll_type: Option(str, description="The type of roll to perform",
                                     choices=['advantage', 'disadvantage', 'flat'], default='flat', required=False),
                   hidden: Option(bool, description="Whether to hide the roll from others", required=False,
                                  default=False)):
        try:
            actual_result, all_rolls, max_result = parse_roll(self.ROLL_TYPES[roll_type] + roll)
            color_green = floor(255 * ((actual_result - 1) / (max_result - 1)))
            color_red = 255 - color_green
            embed = Embed(title=f"Rolled {roll}", colour=Colour.from_rgb(color_red, color_green, 0))
            embed.add_field(name='Result', value=actual_result, inline=True)
            embed.add_field(name='Max', value=max_result, inline=True)
            embed.add_field(name='Roll Type', value=roll_type, inline=False)
            if roll_type in ['advantage', 'disadvantage']:
                embed.add_field(name='All Rolls Performed', value=all_rolls, inline=False)
            embed.set_footer(text=f"Rolled By {ctx.interaction.user.name}")
            await ctx.respond(embed=embed, ephemeral=hidden)
        except RollingError as error:
            await ctx.respond(error.args[0], ephemeral=True)

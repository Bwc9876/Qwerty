from discord.colour import Colour
from discord.commands import slash_command, ApplicationContext, Option
from discord.embeds import Embed
from favicon import get as get_favicon
from requests import get
from requests.exceptions import RequestException, Timeout, ConnectionError
from requests.models import Response

from bot_base.cogs import BaseCog
from bot_settings import DEBUG_GUILDS
from status.models import StatusCogData


class Status(BaseCog):
    cog_data_model = StatusCogData

    @slash_command(name='status', description="Get the status of a website", guild_ids=DEBUG_GUILDS)
    async def status(self, ctx: ApplicationContext, url: Option(str,
                                                                description="The url of the website to check ex: discord.com (omit the https://)")):
        try:
            await ctx.defer()
            response: Response = get(f"https://isitup.org/{url}.json",
                                     headers={'User-Agent': 'https://github.com/lord63/isitup'})
            json_response = response.json()
            response_code = json_response['status_code']
            if response_code == 3:
                await ctx.respond("Invalid Domain")
            else:
                embed = Embed(title=f'Status Of {url}', url=f"https://{url}/")
                if response_code == 1:
                    embed.description = f"{url} is online"
                    embed.colour = Colour.green()
                    embed.add_field(name='Response Time', value=str(json_response['response_time']) + 's')
                    embed.add_field(name='Response Code', value=json_response['response_code'])
                    embed.set_footer(text=f"IP: {json_response['response_ip']}:{json_response['port']}")
                    try:
                        embed.set_thumbnail(url=get_favicon(f'https://{url}/')[0].url)
                    except IndexError:
                        pass
                else:
                    embed.description = f"{url} is offline"
                    embed.colour = Colour.red()
                await ctx.respond(embed=embed)
        except ConnectionError:
            await ctx.respond(
                "There was an error checking the status of the site (this doesn't mean the site is down, we just can't check for some reason)")
        except Timeout:
            await ctx.respond("The request timed out")
        except RequestException as error:
            await ctx.respond(f"There was an error: {str(error)}")

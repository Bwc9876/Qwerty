import base64
import os
from asyncio import create_subprocess_shell, sleep
from io import BytesIO
from pathlib import Path
from socket import gaierror as SocketError
from subprocess import PIPE

import mctools.mclient
from discord import File
from discord.colour import Colour
from discord.commands import slash_command, Option, ApplicationContext, AutocompleteContext, permissions
from discord.embeds import Embed
from discord.role import Role
from discord.utils import basic_autocomplete
from mcstatus.server import MinecraftServer
from mctools import RCONClient

from bot_base.cogs import BaseCog
from bot_settings import DEBUG_GUILDS, OWNER
from minecraft.models import MinecraftCogData

MC_ROOT = os.getenv('MC_ROOT', './')


async def new_profile_autocomplete(ctx: AutocompleteContext):
    return [profile_dir.name for profile_dir in Path(MC_ROOT).iterdir() if profile_dir.is_dir()]


class Minecraft(BaseCog):
    cog_data_model = MinecraftCogData

    REMOVE_FORMATTER = mctools.mclient.BaseClient.REMOVE

    COMMAND_PERMS = (
        ('mc-switch-profile', 'mc-designate-controller', 'mc-exec'),
        ('mc-start', 'mc-stop'),
    )

    def __init__(self, bot):
        super(Minecraft, self).__init__(bot)
        self.mc_port = os.getenv('MC_SERVER_PORT', '25565')
        self.rcon_port = int(os.getenv('MC_RCON_PORT', '25575'))
        self.rcon_password = os.getenv('MC_RCON_PASS', 'rcon')
        self.query = MinecraftServer.lookup(f"127.0.0.1:{self.mc_port}")
        self.mc_start_cmd = os.getenv('MC_START_COMMAND', './start.sh')
        self.display_host = os.getenv('MC_DISPLAY_HOST', '127.0.0.1')
        self.server_proc = None

    def server_is_online(self):
        try:
            return self.server_proc is not None and self.server_proc.returncode is None
        except ProcessLookupError:
            return False

    def get_rcon(self):
        rcon = RCONClient('127.0.0.1', port=self.rcon_port, format_method=self.REMOVE_FORMATTER)
        rcon.login(self.rcon_password)
        return rcon

    async def cog_data_check(self, ctx: ApplicationContext, data: MinecraftCogData):
        cmd_name = ctx.command.qualified_name()
        if cmd_name in self.COMMAND_PERMS[0]:
            if ctx.interaction.user.id == OWNER:
                return True
            else:
                await ctx.respond("This command can only be used by the owner of this bot", ephemeral=True)
                return False
        elif cmd_name in self.COMMAND_PERMS[1]:
            if ctx.interaction.user.id == OWNER or (data.controller_role is not None and ctx.interaction.user.get_role(
                    data.controller_role) is not None):
                return True
            else:
                await ctx.respond("You lack permissions to perform that command", ephemeral=True)
                return False
        else:
            return True

    @slash_command(name="mc-switch-profile", description="Switch The Minecraft Server Profile To Use",
                   guild_ids=DEBUG_GUILDS)
    @permissions.is_user(OWNER)
    async def switch_profile(self, ctx: ApplicationContext,
                             new_profile: Option(str, description="The new profile to use",
                                                 autocomplete=basic_autocomplete(new_profile_autocomplete))):
        if self.server_is_online():
            await ctx.respond("Server is online, stop it first", ephemeral=True)
        else:
            data: MinecraftCogData = await self.load_data(ctx.interaction.guild.id)
            data.active_profile = new_profile
            await self.save_data(data)
            await ctx.respond(f"Switched to {new_profile}")

    @slash_command(name='mc-designate-controller', description="Designate a role to be the controller for the server",
                   guild_ids=DEBUG_GUILDS)
    @permissions.is_user(OWNER)
    async def designate_controller(self, ctx: ApplicationContext,
                                   new_controller: Option(Role, description="The role to designate as controller")):
        data: MinecraftCogData = await self.load_data(ctx.interaction.guild.id)
        data.controller_role = new_controller.id
        await self.save_data(data)
        await ctx.respond("Controller Role Changed")

    @slash_command(name='mc-start', description="Start the minecraft server", guild_ids=DEBUG_GUILDS)
    async def start(self, ctx: ApplicationContext):
        data: MinecraftCogData = await self.load_data(ctx.interaction.guild.id)
        if self.server_is_online():
            await ctx.respond("The server is already online", ephemeral=True)
        else:
            self.server_proc = await create_subprocess_shell(self.mc_start_cmd, stdout=PIPE,
                                                             cwd=f'{MC_ROOT}/{data.active_profile}')
            await ctx.respond(f"Server Started With Profile `{data.active_profile}`")

    @slash_command(name='mc-stop', description="Stop the minecraft server", guild_ids=DEBUG_GUILDS)
    async def stop(self, ctx: ApplicationContext,
                   force: Option(bool, description="force-kill the server instead of letting it exit normally")):
        if self.server_is_online():
            if force:
                try:
                    self.server_proc.kill()
                except ProcessLookupError:
                    pass
                await ctx.respond("Server Force Stopped")
            else:
                await ctx.defer()
                with self.get_rcon() as rcon:
                    rcon.command('stop')
                await sleep(5)
                if self.server_is_online() is False:
                    await ctx.respond("Server Stopped")
                else:
                    await ctx.respond("Server is still online, use `force: True` to force kill")
        else:
            await ctx.respond("The server is already offline, or, it's online but this bot isn't the one that ran it",
                              ephemeral=True)

    @slash_command(name='mc-exec', description="Execute a command on the minecraft server", guild_ids=DEBUG_GUILDS)
    @permissions.is_user(OWNER)
    async def exec(self, ctx: ApplicationContext, command: Option(str, description='The command to execute')):
        if self.server_is_online():
            if command.strip() in ('stop', 'restart'):
                await ctx.respond("Use `/mc-stop` to stop the server", ephemeral=True)
            else:
                with self.get_rcon() as rcon:
                    response = rcon.command(command)
                    if response != '':
                        await ctx.respond("The server responded with: \n```\n" + response + '\n```')
                    else:
                        await ctx.respond("Command Received")
        else:
            await ctx.respond("Server is offline", ephemeral=True)

    @slash_command(name='mc-status', description="Get the status of the server", guild_ids=DEBUG_GUILDS)
    async def status(self, ctx: ApplicationContext):
        data: MinecraftCogData = await self.load_data(ctx.interaction.guild.id)
        embed = Embed()
        embed.title = "Server Status"
        embed.add_field(name="Address", value=f"{self.display_host}", inline=False)
        try:
            stats = await self.query.async_status()
            embed.description = "Server is online"
            embed.colour = Colour.green()
            embed.add_field(name="Profile", value=data.active_profile)
            embed.add_field(name="Version", value=stats.version.name, inline=False)
            embed.add_field(name="Ping", value=str(stats.latency) + " ms", inline=False)
            embed.add_field(name="Players", value=f"{stats.players.online} out of {stats.players.max}", inline=False)
            if stats.favicon is None:
                await ctx.respond(embed=embed)
            else:
                favicon_file = BytesIO()
                decoded = base64.decodebytes(stats.favicon[22:].encode('utf-8'))
                favicon_file.write(decoded)
                favicon_file.seek(0)
                embed.set_thumbnail(url="attachment://server_icon.png")
                await ctx.respond(file=File(favicon_file, filename="server_icon.png"), embed=embed)
                favicon_file.close()
        except (ConnectionError, SocketError):
            embed.description = f"Server is offline, run `/mc-start` to start it"
            embed.add_field(name="Profile", value=data.active_profile)
            embed.colour = Colour.red()
            await ctx.respond(embed=embed)

    @slash_command(name="mc-players", description="Get the players on the server right now", guild_ids=DEBUG_GUILDS)
    async def players(self, ctx: ApplicationContext) -> None:
        if self.server_is_online():
            try:
                query = await self.query.async_query()
                names = '\n'.join(query.players.names)
                if len(names) > 0:
                    await ctx.respond(f"{query.players.online} out of {query.players.max} online:\n```\n{names}\n```")
                else:
                    await ctx.respond("No players online")
            except (ConnectionError, TimeoutError, SocketError):
                await ctx.respond("Server refused query, is query enabled?", ephemeral=True)
        else:
            await ctx.respond("Server is not online", ephemeral=True)

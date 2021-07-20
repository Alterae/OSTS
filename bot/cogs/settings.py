from discord.ext import commands
from importlib import reload
import discord
import inspect
import helpers
import re


class Settings(commands.Cog, description=""):
    def __init__(self, bot):
        self.osts = bot
        self.cog_name = "Settings"
        self.data = helpers.get_toml("data")
        prefix = self.osts.command_prefix

    # ==================================================
    # Unload Event
    # ==================================================
    def cog_unload(self):
        helpers.log(text="Unloaded", cog=self.cog_name)


    # ==================================================
    # Server settings
    # ==================================================
    @commands.command(aliases=["ss"], brief="Change server-specific settings!", help=f"""\
        __**Server Settings**__
        Change server-specific settings to whatever you like!

        __Changing the Bot's Prefix__
        `os.server_settings prefix os.`
        `os.server_settings prefix !`

        __Toggling Invocation Deletion__
        `os.server_settings delete_command`
        """)
    async def server_settings(self, ctx, _one="", _two=""):
        server_data = helpers.get_toml(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await helpers.try_delete(ctx)
    
        if _one == "":
            return await helpers.give_output(
                embed_title = f"the {re.sub(r'_', ' ', inspect.stack()[0][3])} command!",
                embed_content = self.osts.get_command(inspect.stack()[0][3]).help,
                ctx = ctx
            )
    
        # ==================================================
        # If theyre changing the bots prefix
        # ==================================================
        if _one == "prefix":
            previous_prefix = server_data.get("prefix")
            if not previous_prefix:
                previous_prefix = "None"
            server_data["prefix"] = _two

            return await helpers.give_output(
                embed_title = "Alright!",
                embed_content = f"My prefix has been changed from \"{previous_prefix}\" to \"{_two}\"!",
                log_text = f"Changed prefix to {_two}",
                ctx = ctx,
                data = server_data,
                data_file = f"servers/{ctx.guild.id}"
            )

        # ==================================================
        # If theyre toggling invocation deletion
        # ==================================================
        if _one == "delete_command":
            if server_data.get("delete_invocation"):
                server_data["delete_invocation"] = not server_data["delete_invocation"]
            else:
                server_data["delete_invocation"] = True

            return await helpers.give_output(
                embed_title = "Alright!",
                embed_content = f"Command deletion has been {'enabled' if server_data['delete_invocation'] else 'disabled'}!",
                log_text = f"Toggled invocation deletion",
                ctx = ctx,
                data = server_data,
                data_file = f"servers/{ctx.guild.id}"
            )


def setup(bot):
    helpers.log(text="Loaded", cog="Settings")
    bot.add_cog(Settings(bot))
    reload(helpers)
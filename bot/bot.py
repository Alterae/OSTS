from discord.ext import commands
import traceback
import difflib
import discord
import helpers
import re

# ==================================================
# Getting prefixes per-server
# ==================================================
def get_prefix(client, message):
    if message.channel.type not in ["private", "group"]:
        server_data = helpers.get_toml(f"servers/{message.guild.id}")
        user_data = helpers.get_toml(f"users/{message.author.id}")
        if user_data.get("prefix"):
            return user_data["prefix"]
        elif server_data.get("prefix"):
            return server_data["prefix"]
        else:
            return "os."
    else:
        user_data = helpers.get_toml(f"users/{message.author.id}")
        if user_data.get("prefix"):
            return user_data["prefix"]
        else:
            return "os."
        

# ==================================================
# Clear the console
# Init bot
# Grab data
# Grab cogs
# ==================================================
helpers.clear()
osts = commands.Bot(command_prefix = get_prefix, owner_id = 184474965859368960)
data = helpers.get_toml("data")
cogs = data["cogs"]

# ==================================================
# Remove default help command
# ==================================================
# osts.remove_command("help")

# ==================================================
# Load all cogs
# ==================================================
for cog in cogs:
    osts.load_extension(cog)
    helpers.log(f"{cog} loaded")

# ==================================================
# Function for checking if user is a bot owner
# ==================================================
def is_owner(ctx):
    return ctx.author.id in [184474965859368960]



# ==================================================
# When connected
# ==================================================
@osts.event
async def on_connect():
    helpers.log("Connected")
    helpers.log(f"Online on {len(osts.guilds)} servers")

# ==================================================
# When ready
# ==================================================
@osts.event
async def on_ready():
    helpers.log("Ready")
    await osts.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            type = 2,
            name = f"os.help | Or so they say"
        )
    )
    helpers.log("Presence changed")

# ==================================================
# On guild join / leave
# ==================================================
@osts.event
async def on_guild_join(guild):
    if helpers.get_toml(f"servers/{guild.id}") == {}:
        helpers.set_toml(f"servers/{guild.id}", {
            "prefix": "os.",
            "delete_invocation": False
        })
    helpers.log(f"Joined {guild.name}")

@osts.event
async def on_guild_remove(guild):
    helpers.log(f"Left {guild.name}")



# ==================================================
# On a command error
# ==================================================
@osts.event
async def on_command_error(ctx, error):
    # ==================================================
    # If the command they did doesnt exist
    # ==================================================
    if isinstance(error, discord.ext.commands.CommandNotFound):
        embed = helpers.make_embed(
            title = helpers.error_title,
            content = "That command doesn't exist!",
            ctx = ctx
        )

        # ==================================================
        # If we find a command that was a close match
        # Add an embed listing close matches
        # ==================================================
        try:
            if len(difflib.get_close_matches(re.match(rf"{osts.command_prefix}(\S+)", ctx.message.content).groups()[0], [command.name for command in osts.commands], cutoff=0.5)) > 0:
                embed.add_field(
                    name = "Did You Mean...",
                    value = osts.command_prefix + f"\n{osts.command_prefix}".join(difflib.get_close_matches(re.match(rf"{osts.command_prefix}(\S+)", ctx.message.content).groups()[0], [command.name for command in osts.commands], cutoff=0.5)),
                    inline = False
                )
        except: pass

        # ==================================================
        # Send output
        # ==================================================
        return await helpers.give_output(
            embed = embed,
            log_text = f"Tried to do a command that doesnt exist",
            ctx = ctx
        )

    # ==================================================
    # If they don't have permission to do the command
    # ==================================================
    if isinstance(error, discord.ext.commands.MissingPermissions):
        return await helpers.give_output(
            embed_title = helpers.error_title,
            embed_content = "You don't have permission to do that command!",
            log_text = "Tried to do a command without permissions",
            ctx = ctx
        )

    # ==================================================
    # If the command is disabled
    # ==================================================
    if isinstance(error, discord.ext.commands.DisabledCommand):
        return await helpers.give_output(
            embed_title = helpers.error_title,
            embed_content = "That command is disabled!",
            log_text = "Tried to do a disabled command",
            ctx = ctx
        )

    # ==================================================
    # Otherwise, prepare an error output
    # Get bot owner by id
    # ==================================================
    owner = await osts.fetch_user(osts.owner_id)

    # ==================================================
    # Make a big-ass embed with all the error info
    # ==================================================
    embed = helpers.make_embed(
        title="Yikes",
        content="```" + "\n".join(traceback.format_tb(error.original.__traceback__)) + "```",
        ctx = ctx
    )
    embed.add_field(name="Command", value=ctx.message.content.split(" ")[0], inline=True)
    embed.add_field(name="Message", value=ctx.message.content, inline=True)
    embed.add_field(name="Server", value=ctx.guild.name, inline=True)
    embed.add_field(name="Author", value=ctx.author.name, inline=True)
    embed.add_field(name="Error", value=f"`{error.original}`", inline=True)

    # ==================================================
    # Output
    # ==================================================
    await owner.send(embed=embed)
    await helpers.give_output(
        embed_title = helpers.error_title,
        embed_content = "Whatever you did, I got an error!\nI've told my owner about this.",
        log_text = f"Got an error from the {ctx.message.content.split(' ')[0]} command",
        ctx = ctx
    )



# ==================================================
# Reload command (lol copy+pasted from old abacus)
# ==================================================
@osts.command(name="reload", brief="Reload one or all of Abacus' cogs", help="This command is owner-only.\n\nReload all cogs, or reload a specific cog. This refreshes the file and applies any changes made.", hidden=True)
@commands.check(is_owner)
async def _reload(ctx, cog="all"):
    # server_data = helpers.getJson(f"servers/{ctx.guild.id}")
    # if not server_data.get("delete_invocation") in [None, False]: await helpers.tryDelete(ctx)
    
    # ==================================================
    # Get the datafile and load cogs
    # ==================================================
    data = helpers.get_toml("data")
    cogs = data["cogs"]
    log = []

    # ==================================================
    # If no specific cog is given
    # Go through every cog
    # Try to load it - if that fails, try to reload it
    # If *that* fails, throw an error
    # ==================================================
    if cog == "all":
        for extension in cogs:
            try:
                osts.load_extension(extension)
                log.append(f"- **{extension.title()}** loaded successfully")
            except commands.ExtensionAlreadyLoaded:
                osts.reload_extension(extension)
                log.append(f"- **{extension.title()}** reloaded successfully")
            except commands.ExtensionNotFound:
                await helpers.give_output(
                    embed_title = helpers.error_title,
                    embed_content = f"I couldn't find a cog with the name \"{extension}\"!",
                    ctx = ctx
                )

        await helpers.give_output(
            embed_title = "Success!",
            embed_content = "\n".join(log),
            log_text = "Reloaded all cogs",
            ctx = ctx
        )
    
    # ==================================================
    # Otherwise (they gave a specific cog)
    # Load/reload the specific cog and send output
    # ==================================================
    else:
        _type = "loaded"
        try:
            osts.load_extension(cog)
        except commands.ExtensionAlreadyLoaded:
            osts.reload_extension(cog)
            _type="reloaded"
        except commands.ExtensionNotFound:
            await helpers.give_output(
                embed_title = helpers.error_title,
                embed_content = f"I couldn't find a cog with the name \"{cog}\"",
                ctx = ctx
            )

        await helpers.give_output(
            embed_title = "Success!",
            embed_content = f"**{cog.title()}** {_type} successfully!",
            log_text = f"Reloaded {cog}",
            ctx = ctx
        )

# ==================================================
# If >>reload gets an error
# ==================================================
@_reload.error
async def _reload_error(ctx, error):
    # ==================================================
    # If the user isnt the bot owner (failed the check)
    # Say so and log to console
    # ==================================================
    if isinstance(error, commands.CheckFailure):
        # await helpers.tryDelete(ctx)
        await helpers.give_output(
            embed_title = helpers.error_title,
            embed_content = "Only the bot owner can reload cogs!"
        )
        embed = helpers.make_embed(title="Whoops!", description="Only the bot owner can reload cogs!", ctx=ctx)
        await ctx.send(embed=embed)
        helpers.log(text="Tried to reload cogs", ctx=ctx)



# ==================================================
# Grab the bots token from a file
# Run the bot
# ==================================================
tokens = helpers.get_json("../../../../bot_tokens")
osts.run(tokens["OSTS"])
from time import localtime, strftime
from datetime import datetime
import discord
import toml
import json
import os
import re


# ==================================================
# Basic variables
# ==================================================
error_title = "Whoops!"
success_title = "Alright!"
linebreak = "\n"


def success_title(ctx):
    user_data = get_toml(f"users/{ctx.author.id}")
    if user_data.get("success title"):
        return user_data["success title"]
    else:
        return "Alright!"

def error_title(ctx):
    user_data = get_toml(f"users/{ctx.author.id}")
    if user_data.get("error title"):
        return user_data["error title"]
    else:
        return "Whoops!"


# ==================================================
# Clearing console
# ==================================================
def clear():
    if os.name == "nt":
        return os.system("cls")
    else:
        return os.system("clear")


# ==================================================
# Getting the current time as a string
# ==================================================
def get_time():
    return strftime("%m/%d/%Y %I:%M:%S %p", localtime())


# ==================================================
# Getting and setting JSON data
# ==================================================
def get_json(file):
    try:
        with open(f"./data/{file}.json", "r") as data_file:
            return json.loads(data_file.read())
    except IOError:
        return {}

def set_json(file, data):
    with open(f"./data/{file}.json", "w+") as data_file:
        return data_file.write(json.dumps(data))

# ==================================================
# Getting and setting TOML data
# ==================================================
def get_toml(file):
    try:
        with open(f"./data/{file}.toml", "r", encoding="utf-8") as data_file:
            return toml.loads(data_file.read())
    except IOError:
        return {}

def set_toml(file, data):
    with open(f"./data/{file}.toml", "w+", encoding="utf-8") as data_file:
        return data_file.write(toml.dumps(data))


# ==================================================
# Deleting messages
# ==================================================
async def try_delete(ctx):
    try:
        await ctx.message.delete()
    except:
        pass


# ==================================================
# Making embeds
# ==================================================
def make_embed(
        ctx,
        title = None,
        content = None):
    
    # ==================================================
    # Trim whitespace from content
    # Capitalize the title
    # ==================================================
    content = re.sub(r"\t", " ", content)
    while "  " in content:
        content = content.replace("  ", " ")

    title = title.capitalize()

    # ==================================================
    # Grab user color if it exists, otherwise use default
    # ==================================================
    user_data = get_toml(f"users/{ctx.author.id}")
    if user_data.get("color"):
        color = int("0x" + user_data.get("color"), 0)
    else:
        color = 0xFFFF00

    # ==================================================
    # Create an embed
    # ==================================================
    output_embed = discord.Embed(
        title = title,
        description = content,
        color = color
    )

    # ==================================================
    # Add author
    # ==================================================
    output_embed.set_author(
        name = ctx.author.nick if ctx.author.nick else ctx.author.name,
        icon_url = ctx.author.avatar_url
    )

    # ==================================================
    # Set timestamp
    # ==================================================
    output_embed.timestamp = datetime.utcnow()

    return output_embed


# ==================================================
# Giving output
# ==================================================
async def give_output(
        embed_title = None,
        embed_content = None,
        embed = None,
        log_text = None,
        cog = "OSTS",
        ctx = None,
        data = None,
        data_file = "data"):

    # ==================================================
    # Set data
    # ==================================================
    if data:
        set_toml(data_file, data)

    # ==================================================
    # If an embed isnt given, create one
    # ==================================================
    if not embed:
        embed = make_embed(
            title = embed_title,
            content = embed_content,
            ctx = ctx
        )

    # ==================================================
    # Send the embed
    # ==================================================
    try:
        await ctx.send(embed = embed)
    except discord.Forbidden:
        return log(
            text = "Didn't have permission to send a message",
            cog = cog,
            ctx = ctx
        )

    # ==================================================
    # Output to console if log text given
    # ==================================================
    if log_text:
        log(
            text = log_text,
            cog = cog,
            ctx = ctx
        )

    return True


# ==================================================
# Logging to console
# ==================================================
def log(
        text,
        cog = "OSTS",
        ctx = None):

    if ctx:
        author_text = f"{ctx.author.name} in #{ctx.channel.name}"
        output = f"[{get_time()}] [{cog}] {'.' * (15 - len(cog))} [{ctx.guild.name}] {'.' * (30 - len(ctx.guild.name))} [{author_text}] {'.' * (50 - len(author_text))} {text}"
    else:
        output = f"[{get_time()}] [{cog}] {'.' * (15 - len(cog))} {text}"

    output = output.upper()
    return print(output)

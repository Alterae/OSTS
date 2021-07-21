from discord.ext import commands
from importlib import reload
import discord
import inspect
import helpers
import re


class Halls(commands.Cog, description=""):
	def __init__(self, bot):
		self.osts = bot
		self.cog_name = "Halls"
		self.data = helpers.get_toml("data")

	# ==================================================
	# Unload Event
	# ==================================================
	def cog_unload(self):
		helpers.log(text="Unloaded", cog=self.cog_name)


	# ==================================================
	# 
	# ==================================================
	@commands.command(brief="Add, edit, list, and remove halls!", help="""\
		__**Halls**__
		Add, edit, list, or remove halls!

		__Listing Halls__
		`[prefix]halls list`

		__Adding Halls__
		`[prefix]halls add Fame`
		`[prefix]halls add Shame`

		__Editing Halls__
		`[prefix]halls edit Fame requirement 5`
		`[prefix]halls edit Fame format [author]: [content]`

		__Removing Halls__
		`[prefix]halls remove Fame`
		""")
	async def halls(self, ctx, _action="", _hall="", _item="", *, _value=""):
		server_data = helpers.get_toml(f"servers/{ctx.guild.id}")
		if server_data.get("delete_invocation") == True:
			await helpers.tryDelete(ctx)
	
		if _action not in ["list", "edit", "add", "remove"]:
			return await helpers.give_output(
				embed_title = f"the {re.sub(r'_', ' ', inspect.stack()[0][3])} command!",
				embed_content = re.sub(r"\[prefix\]", self.osts.command_prefix, self.osts.get_command(inspect.stack()[0][3]).help),
				ctx = ctx
			)

		items = ["emoji", "requirement", "channel", "format", "proxied", "announcement", "removal announcement"]

		# ==================================================
		# If they want to list halls
		# ==================================================
		if _action == "list":
			if not server_data.get("halls") or server_data.get("halls") == {}:
				return await helpers.give_output(
					embed_title = helpers.error_title,
					embed_content = f"This server doesn't have any halls!\nAdd some with `{self.osts.command_prefix}halls add`",
					ctx = ctx
				)

			embed = helpers.make_embed(
				title = "Alright!",
				content = "Here are all of this server's halls!",
				ctx = ctx
			)

			for hall, hall_data in server_data["halls"].items():
				embed.add_field(
					name = hall,
					value = f"**Emoji:** {hall_data['emoji']}\n**Requirement:** {hall_data['requirement']}\n**Channel:** {hall_data['channel']}"
				)

			return await helpers.give_output(
				embed = embed,
				log_text = f"Listed halls",
				ctx = ctx
			)

		# ==================================================
		# If they want to add a hall
		# ==================================================
		if _action == "add":
			if _hall == "":
				return await helpers.give_output(
					embed_title = helpers.error_title,
					embed_content = f"Please enter a hall name!\n`{self.osts.command_prefix}halls add Fame`",
					ctx = ctx
				)

			if not server_data.get("halls"):
				server_data["halls"] = {}

			server_data["halls"][_hall] = {
				"emoji": None,
				"requirement": 4,
				"channel": None,
				"format": "**[author]**\n[message]\n\n[attachments]",
				"proxied": False,
				"announcement": f"**[author]** was added to the hall of {_hall}!",
				"removal announcement": f"**[author]** was removed from the hall of {_hall}",
				"messages": []
			}

			embed = helpers.make_embed(
				title = helpers.success_title,
				content = f"Successfully added the hall of {_hall}!",
				ctx = ctx
			)

			for item in items:
				embed.add_field(
					name = item.title(),
					value = server_data["halls"][_hall][item],
					inline = True
				)

			return await helpers.give_output(
				embed = embed,
				log_text = f"Created the hall of {_hall}",
				ctx = ctx,
				data = server_data,
				data_file = f"servers/{ctx.guild.id}"
			)

		# ==================================================
		# If they want to edit a hall
		# ==================================================
		if _action == "edit":
			if not server_data.get("halls") or server_data.get("halls") == {}:
				return await helpers.give_output(
					embed_title = helpers.error_title,
					embed_content = f"This server doesn't have any halls!\nAdd some with `{self.osts.command_prefix}halls add`",
					ctx = ctx
				)

			if not _hall in server_data["halls"].keys():
				return await helpers.give_output(
					embed_title = helpers.error_title,
					embed_content = f"I couldn't find a hall with that name!\nMake sure to use the right capitalization!",
					ctx = ctx
				)

			if _item == "":
				embed = helpers.make_embed(
					title = helpers.success_title,
					content = f"Here's the hall of {_hall}!",
					ctx = ctx
				)

				for item in items:
					embed.add_field(
						name = item.title(),
						value = server_data["halls"][_hall][item],
						inline = True
					)

				return await helpers.give_output(
					embed = embed,
					log_text = f"Got information on the hall of {_hall}",
					ctx = ctx
				)

			if _item not in items:
				return await helpers.give_output(
					embed_title = helpers.error_title,
					embed_content = f"Please give a valid item to edit!\n\nValid items are:\n{'\n'.join(items[:-1])}\nremoval_announcement",
					ctx = ctx
				)

			if _item != "proxied" and _value == "":
				return await helpers.give_output(
					embed_title = helpers.error_title,
					embed_content = f"Please give a value for the item you wish to edit!",
					ctx = ctx
				)

			if _item in ["format", "announcement", "removal announcement", "removal_announcement"]:
				_item = _item.replace("_", " ")

				server_data["halls"][_hall][_item] = _value

				return await helpers.give_output(
					embed_title = helpers.success_title,
					embed_content = f"Successfully changed the hall of {_hall}'s {_item} to {_value}!",
					log_text = f"Changed the hall of {_hall}'s {_item}",
					ctx = ctx,
					data = server_data,
					data_file = f"servers/{ctx.guild.id}"
				)

			# if _item == "emoji":
				# Try to react to the original message with the emoji
				# If it works, cool
				# If it fails, its an invalid emoji

			if _item == "requirement":
				try:
					_value = int(_value)
				except:
					return await helpers.give_output(
						embed_title = helpers.error_title,
						embed_content = f"Please give a valid number for the hall requirement!",
						ctx = ctx
					)
				
				server_data["halls"][_hall][_item] = _value

				return await helpers.give_output(
					embed_title = helpers.success_title,
					embed_content = f"Successfully changed the hall of {_hall}'s {_item} to {_value}!",
					log_text = f"Changed the hall of {_hall}'s {_item}",
					ctx = ctx,
					data = server_data,
					data_file = f"servers/{ctx.guild.id}"
				)

			# if _item == "channel":
				# Try to get the channel by id
				# If it works, cool
				# If it fails, its an invalid channel

			if _item == "proxied":
				server_data["halls"][_hall][_item] = not server_data["halls"][_hall][_item]

				return await helpers.give_output(
					embed_title = helpers.success_title,
					embed_content = f"Proxying for the hall of {_hall} has been changed to {server_data['halls'][_hall][_item]}!",
					log_text = f"Changed the hall of {_hall}'s proxying",
					ctx = ctx,
					data = server_data,
					data_file = f"servers/{ctx.guild.id}"
				)

		# ==================================================
		# If they want to remove a hall
		# ==================================================
		if _action == "remove":
			if not server_data.get("halls") or server_data.get("halls") == {}:
				return await helpers.give_output(
					embed_title = helpers.error_title,
					embed_content = f"This server doesn't have any halls!\nAdd some with `{self.osts.command_prefix}halls add`",
					ctx = ctx
				)

			if not _hall in server_data["halls"].keys():
				return await helpers.give_output(
					embed_title = helpers.error_title,
					embed_content = f"I couldn't find a hall with that name!\nMake sure to use the right capitalization!",
					ctx = ctx
				)

			del server_data["halls"][_hall]

			return await helpers.give_output(
				embed_title = helpers.success_title,
				embed_content = f"Removed the hall of {_hall}",
				log_text = f"Removed the hall of {_hall}",
				ctx = ctx,
				data = server_data,
				data_file = f"servers/{ctx.guild.id}"
			)


def setup(bot):
	helpers.log(text="Loaded", cog="Halls")
	bot.add_cog(Halls(bot))
	reload(helpers)
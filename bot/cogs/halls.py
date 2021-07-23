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
	# Reaction event
	# ==================================================
	async def reaction_event(self, payload):
		# ==================================================
		# Get original channel and message from payload
		# Get reaction counts
		# ==================================================
		original_channel = self.osts.get_channel(payload.channel_id)
		original_message = await original_channel.fetch_message(payload.message_id)
		reaction_count = None
		for reaction in original_message.reactions:
			if str(reaction.emoji) == str(payload.emoji):
				reaction_count = reaction.count

		if not reaction_count:
			reaction_count = 0

		# ==================================================
		# Grab the servers data
		# ==================================================
		server_data = helpers.get_toml(f"servers/{original_message.guild.id}")

		# ==================================================
		# If the server doesnt have any halls, return
		# ==================================================
		if not server_data.get("halls") or server_data.get("halls") == {}:
			return False

		# ==================================================
		# Iterate through halls and get the hall that matches 
		# the reactions emoji
		# ==================================================
		emoji_is_hall_emoji = False
		message_stored = False
		hall = None
		hall_data = None
		for _hall, _hall_data in server_data["halls"].items():
			if _hall_data["emoji"] == str(payload.emoji):
				emoji_is_hall_emoji = True
				hall = _hall
				hall_data = _hall_data
			for _message in _hall_data["messages"]:
				if _message["original message id"] == original_message.id:
					message_stored = True

		# ==================================================
		# If there isnt a hall that matches the reaction emoji
		# Return
		# ==================================================
		if not emoji_is_hall_emoji:
			return False

		# ==================================================
		# If the hall doesnt have a channel set, return
		# ==================================================
		if hall_data["channel"] == "None":
			return False

		# ==================================================
		# If the reaction count is greater than the requirement
		# And the server data doesnt have the message stored
		# ==================================================
		if reaction_count >= server_data["halls"][hall]["requirement"] and not message_stored:
			# ==================================================
			# Announce that they got into a hall
			# ==================================================
			announcement_message = re.sub(r"\[author\]", original_message.author.name, server_data["halls"][hall]["announcement"])
			announcement_message = re.sub(r"\[hall\]", hall, announcement_message)
			announcement_message = re.sub(r"\[channel\]", original_message.channel.name, announcement_message)
			await original_message.channel.send(announcement_message)

			hall_channel = self.osts.get_channel(int(server_data["halls"][hall]["channel"][2:-1]))
		
			# ==================================================
			# Send the message in the hall w/o proxy
			# ==================================================
			if not server_data["halls"][hall]["proxied"]:
				hall_message = re.sub(r"\[author\]", original_message.author.name, server_data["halls"][hall]["format"])
				hall_message = re.sub(r"\[message\]", original_message.content, hall_message)
				hall_message = re.sub(r"\[attachments\]", "\n".join([(f"|| {attachment.url} ||" if "SPOILER_" in attachment.url else attachment.url) for attachment in original_message.attachments]), hall_message)
				hall_message_obj = await hall_channel.send(hall_message)
			else:
				# ==================================================
				# Try to get channel webhooks
				# Error if missing permissions
				# ==================================================
				try:
					channel_webhooks = await hall_channel.webhooks()
				except:
					embed = helpers.make_embed(
						title = helpers.error_title(ctx),
						content = f"You have proxying enabled for the {hall} hall, but I don't have permission to access and create webhooks for the channel you have set!\nI need permissions, or you can set tell me to put them in a different channael.",
						ctx = original_message
					)

					await original_message.channel.send(embed=embed)

				# ==================================================
				# Check for a webhook, create one if it doesnt exist
				# ==================================================
				has_webhook = False
				for _webhook in channel_webhooks:
					if _webhook.user.name == self.osts.user.name:
						has_webhook = True
						webhook = _webhook

				if not has_webhook:
					webhook = await hall_channel.create_webhook(name="OSTS Webhook")

				# ==================================================
				# Create an array of files
				# ==================================================
				files = [await attch.to_file() for attch in original_message.attachments]

				# ==================================================
				# Try to send the message
				# If it fails (files too big), send files as urls
				# ==================================================
				try:
					hall_message_obj = await webhook.send(original_message.content, username=original_message.author.name, avatar_url=original_message.author.avatar_url, files=files, wait=True)
				except:
					hall_message_obj = await webhook.send(original_message.content + "\n\n" + "\n".join([attch.url for attch in original_message.attachments]), username=original_message.author.name, avatar_url=original_message.author.avatar_url, wait=True)

			# ==================================================
			# Add the message to the channels message list
			# ==================================================
			server_data["halls"][hall]["messages"].append({
				"original message id": original_message.id,
				"hall message id": hall_message_obj.id,
				"author id": original_message.author.id
			})

			# ==================================================
			# Log to console
			# Save data
			# ==================================================
			helpers.log(
				"Got put in a hall",
				cog = self.cog_name,
				ctx = original_message
			)

			helpers.set_toml(f"servers/{original_message.guild.id}", server_data)

		# ==================================================
		# If the reaction count is less than the requirement
		# And the server data has the message stored
		# ==================================================
		if reaction_count < server_data["halls"][hall]["requirement"] and message_stored:
			# ==================================================
			# Announce that they got removed from the hall
			# ==================================================
			announcement_message = re.sub(r"\[author\]", original_message.author.name, server_data["halls"][hall]["removal announcement"])
			announcement_message = re.sub(r"\[hall\]", hall, announcement_message)
			announcement_message = re.sub(r"\[channel\]", original_message.channel.name, announcement_message)
			await original_message.channel.send(announcement_message)

			# ==================================================
			# Remove the message from the halls data
			# ==================================================
			for i in range(len(server_data["halls"][hall]["messages"])):
				if server_data["halls"][hall]["messages"][i]["original message id"] == original_message.id:
					hall_message_id = server_data["halls"][hall]["messages"][i]["hall message id"]
					author_id = server_data["halls"][hall]["messages"][i]["author id"]
					server_data["halls"][hall]["messages"].pop(i)
					break

			# ==================================================
			# Delete the actual message
			# ==================================================
			hall_channel = self.osts.get_channel(int(server_data["halls"][hall]["channel"][2:-1]))
			hall_message = await hall_channel.fetch_message(hall_message_id)
			await hall_message.delete()

			# ==================================================
			# Log to console
			# Save data
			# ==================================================
			helpers.log(
				"Got removed from a hall",
				cog = self.cog_name,
				ctx = original_message
			)

			helpers.set_toml(f"servers/{original_message.guild.id}", server_data)

	
	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		await self.reaction_event(payload)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		await self.reaction_event(payload)
	
	
	# ==================================================
	# Halls command
	# ==================================================
	@commands.command(brief="Add, edit, list, and remove halls!", help="""\
		__**Halls**__
		Add, edit, list, or remove halls!

		__Listing Halls__
		`[prefix]halls list`

		__Adding Halls__
		`[prefix]halls add "Hall of Fame"`
		`[prefix]halls add "Hall of Shame"`

		__Editing Halls__
		`[prefix]halls edit "Hall of Fame" requirement 5`
		`[prefix]halls edit "Hall of Fame" Fame format [author]: [content]`

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
				embed_content = re.sub(r"\[prefix\]", self.osts.command_prefix(self.osts, ctx.message), self.osts.get_command(inspect.stack()[0][3]).help),
				ctx = ctx
			)

		items = ["emoji", "requirement", "channel", "format", "proxied", "announcement", "removal announcement"]

		# ==================================================
		# If they want to list halls
		# ==================================================
		if _action == "list":
			# ==================================================
			# If the server doesnt have any halls
			# Say so
			# ==================================================
			if not server_data.get("halls") or server_data.get("halls") == {}:
				return await helpers.give_output(
					embed_title = helpers.error_title(ctx),
					embed_content = f"This server doesn't have any halls!\nAdd some with `{self.osts.command_prefix(self.osts, ctx.message)}halls add`",
					ctx = ctx
				)

			# ==================================================
			# Make an embed listing every hall
			# ==================================================
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

			# ==================================================
			# Send it
			# ==================================================
			return await helpers.give_output(
				embed = embed,
				log_text = f"Listed halls",
				cog = self.cog_name,
				ctx = ctx
			)

		# ==================================================
		# Check if they have manage guild permissions
		# ==================================================
		if not ctx.author.guild_permissions.manage_guild:
			return await helpers.give_output(
				embed_title = helpers.error_title(ctx),
				embed_content = "You don't have permission for this!\nOnly users with the manage guild permission can do that.",
				ctx = ctx
			)

		# ==================================================
		# If they want to add a hall
		# ==================================================
		if _action == "add":
			# ==================================================
			# If they didnt enter a hall name
			# Error
			# ==================================================
			if _hall == "":
				return await helpers.give_output(
					embed_title = helpers.error_title(ctx),
					embed_content = f"Please enter a hall name!\n`{self.osts.command_prefix(self.osts, ctx.message)}halls add Fame`",
					ctx = ctx
				)

			if not server_data.get("halls"):
				server_data["halls"] = {}

			# ==================================================
			# Create the hall with default values
			# ==================================================
			server_data["halls"][_hall] = {
				"emoji": "None",
				"requirement": 4,
				"channel": "None",
				"format": "**[author]**\n[message]\n\n[attachments]",
				"proxied": False,
				"announcement": f"**[author]** was added to the {_hall}!",
				"removal announcement": f"**[author]** was removed from the {_hall}!",
				"messages": []
			}

			# ==================================================
			# Make an embed displaying all the hall info
			# ==================================================
			embed = helpers.make_embed(
				title = helpers.success_title(ctx),
				content = f"Successfully added the {_hall} hall!",
				ctx = ctx
			)

			for item in items:
				embed.add_field(
					name = item.title(),
					value = server_data["halls"][_hall][item],
					inline = True
				)

			# ==================================================
			# Send it
			# ==================================================
			return await helpers.give_output(
				embed = embed,
				log_text = f"Created the {_hall} hall",
				ctx = ctx,
				cog = self.cog_name,
				data = server_data,
				data_file = f"servers/{ctx.guild.id}"
			)

		# ==================================================
		# If they want to edit a hall
		# ==================================================
		if _action == "edit":
			# ==================================================
			# If the server doesnt have any halls
			# Say so
			# ==================================================
			if not server_data.get("halls") or server_data.get("halls") == {}:
				return await helpers.give_output(
					embed_title = helpers.error_title(ctx),
					embed_content = f"This server doesn't have any halls!\nAdd some with `{self.osts.command_prefix(self.osts, ctx.message)}halls add`",
					ctx = ctx
				)

			# ==================================================
			# If the given hall isnt in the servers hall list
			# Say so
			# ==================================================
			if not _hall in server_data["halls"].keys():
				return await helpers.give_output(
					embed_title = helpers.error_title(ctx),
					embed_content = f"I couldn't find a hall with that name!\nMake sure to use the right capitalization!",
					ctx = ctx
				)

			# ==================================================
			# If they didnt give anything to edit
			# Just give them the halls information
			# ==================================================
			if _item == "":
				embed = helpers.make_embed(
					title = helpers.success_title(ctx),
					content = f"Here's the {_hall} hall!",
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
					log_text = f"Got information on the {_hall} hall",
					cog = self.cog_name,
					ctx = ctx
				)

			# ==================================================
			# If the item they gave to edit isnt a valid item
			# Say so
			# ==================================================
			if _item not in items:
				return await helpers.give_output(
					embed_title = helpers.error_title(ctx),
					embed_content = f"Please give a valid item to edit!\n\nValid items are:\n{helpers.linebreak.join(items[:-1])}\nremoval_announcement",
					ctx = ctx
				)

			# ==================================================
			# If they didnt give a proper value for the given item
			# Say so
			# ==================================================
			if _item != "proxied" and _value == "":
				return await helpers.give_output(
					embed_title = helpers.error_title(ctx),
					embed_content = f"Please give a value for the item you wish to edit!",
					ctx = ctx
				)

			# ==================================================
			# If the item they gave is one of the formatting ones
			# Just set the value and output, nice and ez
			# ==================================================
			if _item in ["format", "announcement", "removal announcement", "removal_announcement"]:
				_item = _item.replace("_", " ")

				server_data["halls"][_hall][_item] = _value

				return await helpers.give_output(
					embed_title = helpers.success_title(ctx),
					embed_content = f"Successfully changed the {_hall} hall's {_item} to {_value}!",
					log_text = f"Changed the {_hall} hall's {_item}",
					ctx = ctx,
					cog = self.cog_name,
					data = server_data,
					data_file = f"servers/{ctx.guild.id}"
				)

			# ==================================================
			# If the item they gave is the emoji
			# Validate the emoji by reacting to the message
			# Set data
			# ==================================================
			if _item == "emoji":
				try:
					await ctx.message.add_reaction(_value)
					await ctx.message.remove_reaction(_value, self.osts.user)
				except:
					return await helpers.give_output(
						embed_title = helpers.error_title(ctx),
						embed_content = f"Please give a valid emoji!",
						ctx = ctx
					)

				server_data["halls"][_hall][_item] = str(_value)

				return await helpers.give_output(
					embed_title = helpers.success_title(ctx),
					embed_content = f"Successfully changed the heall of {_hall}'s {_item} to {_value}!",
					log_text = f"Changed the {_hall} hall's {_item}",
					ctx = ctx,
					cog = self.cog_name,
					data = server_data,
					data_file = f"servers/{ctx.guild.id}"
				)

			# ==================================================
			# If the item they gave is the requirement
			# Check if its a valid integer
			# Set data
			# ==================================================
			if _item == "requirement":
				try:
					_value = int(_value)
				except:
					return await helpers.give_output(
						embed_title = helpers.error_title(ctx),
						embed_content = f"Please give a valid number for the hall requirement!",
						ctx = ctx
					)
				
				server_data["halls"][_hall][_item] = _value

				return await helpers.give_output(
					embed_title = helpers.success_title(ctx),
					embed_content = f"Successfully changed the {_hall} hall's {_item} to {_value}!",
					log_text = f"Changed the {_hall} hall's {_item}",
					ctx = ctx,
					cog = self.cog_name,
					data = server_data,
					data_file = f"servers/{ctx.guild.id}"
				)

			# ==================================================
			# If the item they gave is the channel
			# Try to fetch the channel to validate it exists
			# Set data
			# ==================================================
			if _item == "channel":
				try:
					channel = ctx.guild.get_channel(int(_value[2:-1]))
				except:
					return await helpers.give_output(
						embed_title = helpers.error_title(ctx),
						embed_content = f"Please give a valid chanenl for the hall!",
						ctx = ctx
					)

				server_data["halls"][_hall][_item] = _value

				return await helpers.give_output(
					embed_title = helpers.success_title(ctx),
					embed_content = f"Successfully changed the {_hall} hall's {_item} to {_value}!",
					log_text = f"Changed the {_hall} hall's {_item}",
					ctx = ctx,
					cog = self.cog_name,
					data = server_data,
					data_file = f"servers/{ctx.guild.id}"
				)	

			# ==================================================
			# If the item they gave is the proxied item
			# Just toggle it
			# ==================================================
			if _item == "proxied":
				server_data["halls"][_hall][_item] = not server_data["halls"][_hall][_item]

				return await helpers.give_output(
					embed_title = helpers.success_title(ctx),
					embed_content = f"Proxying for the {_hall} hall has been changed to {server_data['halls'][_hall][_item]}!",
					log_text = f"Changed the {_hall} hall's proxying",
					ctx = ctx,
					cog = self.cog_name,
					data = server_data,
					data_file = f"servers/{ctx.guild.id}"
				)

		# ==================================================
		# If they want to remove a hall
		# ==================================================
		if _action == "remove":
			if not server_data.get("halls") or server_data.get("halls") == {}:
				return await helpers.give_output(
					embed_title = helpers.error_title(ctx),
					embed_content = f"This server doesn't have any halls!\nAdd some with `{self.osts.command_prefix(self.osts, ctx.message)}halls add`",
					ctx = ctx
				)

			if not _hall in server_data["halls"].keys():
				return await helpers.give_output(
					embed_title = helpers.error_title(ctx),
					embed_content = f"I couldn't find a hall with that name!\nMake sure to use the right capitalization!",
					ctx = ctx
				)

			del server_data["halls"][_hall]

			return await helpers.give_output(
				embed_title = helpers.success_title(ctx),
				embed_content = f"Removed the {_hall} hall",
				log_text = f"Removed the {_hall} hall",
				ctx = ctx,
				cog = self.cog_name,
				data = server_data,
				data_file = f"servers/{ctx.guild.id}"
			)


def setup(bot):
	helpers.log(text="Loaded", cog="Halls")
	bot.add_cog(Halls(bot))
	reload(helpers)
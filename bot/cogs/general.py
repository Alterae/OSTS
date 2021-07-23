from discord.ext import commands
from importlib import reload
import discord
import inspect
import helpers
import random
import re


class General(commands.Cog, description="General commands and utilities!"):
	def __init__(self, bot):
		self.osts = bot
		self.cog_name = "General"
		self.data = helpers.get_toml("data")

	# ==================================================
	# Unload Event
	# ==================================================
	def cog_unload(self):
		helpers.log(text="Unloaded", cog=self.cog_name)


	# ==================================================
	# Choose command
	# ==================================================
	@commands.command(brief="I'll make a choice for you!", help="""\
		__**Choosing**__
		Have me choose from a list of comma seperated values for you!

		`[prefix]choose option one, option two, option three`
		""")
	async def choose(self, ctx, *, _one=""):
		server_data = helpers.get_toml(f"servers/{ctx.guild.id}")
		if server_data.get("delete_invocation") == True:
			await helpers.tryDelete(ctx)
	
		if _one == "" or len(_one.split(", ")) == 1:
			return await helpers.give_output(
				embed_title = f"the {re.sub(r'_', ' ', inspect.stack()[0][3])} command!",
				embed_content = re.sub(r"\[prefix\]", self.osts.command_prefix(self.osts, ctx.message), self.osts.get_command(inspect.stack()[0][3]).help),
				ctx = ctx
			)
	
		choice = random.choice(_one.split(", "))

		return await helpers.give_output(
			embed_title = choice,
			embed_content = f"Out of {', '.join(_one.split(', ')[:-1])}, and {_one.split(', ')[-1]}, I choose {choice}",
			log_text = f"Made a choice",
			ctx = ctx,
			cog = self.cog_name
		)


	# ==================================================
	# Roll command
	# ==================================================
	@commands.command(brief="Roll some die!", help="""\
		__**Rolling**__
		Rolling dice, D&D style!

		__Basics__
		`[prefix]roll 1d20` - rolls 1 dice with 20 sides
		`[prefix]roll 5d6` - rolls 5 dice with 6 sides

		__Modifiers__
		`[prefix]roll 1d20+5` - rolls a dice with 20 sides, then adds 5
		`[prefix]roll 5d6+1` - rolls 5 dice with 6 sides, then adds 1 to the total
		""")
	async def roll(self, ctx, _one=""):
		server_data = helpers.get_toml(f"servers/{ctx.guild.id}")
		if server_data.get("delete_invocation") == True:
			await helpers.tryDelete(ctx)
	
		if _one == "":
			return await helpers.give_output(
				embed_title = f"the {re.sub(r'_', ' ', inspect.stack()[0][3])} command!",
				embed_content = re.sub(r"\[prefix\]", self.osts.command_prefix(self.osts, ctx.message), self.osts.get_command(inspect.stack()[0][3]).help),
				ctx = ctx
			)
	
		try:
			amount = int(_one.split("d")[0])
			size = _one.split("d")[1]
			mod = 0
			if "+" in size:
				modifier = int(size.split("+")[1])
				size = int(size.split("+")[0])
			size = int(size)
		except:
			return await helpers.give_output(
				embed_title = helpers.error_title,
				embed_content = "Please give a valid dice to roll!",
				ctx = ctx
			)

		rolls = []

		for i in range(amount):
			rolls.append(random.randint(1, size))

		embed = helpers.make_embed(
			title = f"Rolled {amount}d{size}{f'+{mod}' if mod != 0 else ''}",
			content = ", ".join([str(roll) for roll in rolls]) if len(", ".join([str(roll) for roll in rolls])) < 4096 else "Rolls too big to display!",
			ctx = ctx
		)

		embed.add_field(
			name = "Total",
			value = sum(rolls) + mod
		)

		return await helpers.give_output(
			embed = embed,
			log_text = f"Rolled {amount}d{size}{f'+{mod}' if mod != 0 else ''}",
			cog = self.cog_name,
			ctx = ctx
		)


	# ==================================================
	# 
	# ==================================================
	@commands.command(brief="Invite me to your server!", help="""\
		__**Getting an Invite**__
		`[prefix]invite`
		""")
	async def invite(self, ctx, _one=""):
		server_data = helpers.get_toml(f"servers/{ctx.guild.id}")
		if server_data.get("delete_invocation") == True:
			await helpers.tryDelete(ctx)
	
		return await helpers.give_output(
			embed_title = helpers.success_title,
			embed_content = f"https://discord.com/oauth2/authorize?client_id=651246752954974229&permissions=8&scope=bot",
			log_text = "Got my invite link",
			ctx = ctx,
			cog = self.cog_name
		)


def setup(bot):
	helpers.log(text="Loaded", cog="General")
	bot.add_cog(General(bot))
	reload(helpers)
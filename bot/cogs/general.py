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
	@commands.command(brief="", help="""\
		__Choosing__
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
				embed_content = re.sub(r"\[prefix\]", self.osts.command_prefix, self.osts.get_command(inspect.stack()[0][3]).help),
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


def setup(bot):
	helpers.log(text="Loaded", cog="General")
	bot.add_cog(General(bot))
	reload(helpers)
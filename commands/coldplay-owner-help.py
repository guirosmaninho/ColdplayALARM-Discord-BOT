import discord
from discord.ext import commands
import datetime
import pytz
import main

TIMEZONE = "Europe/Lisbon"


class OwnerHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coldplay-owner-help")
    async def owner_help(self, ctx):
        """
        Sends a list of all hidden commands.
        """
        embed = discord.Embed(
            title=f"{main.get_random_emoji()} **{self.bot.user.name}**'s Hidden Command List",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(pytz.timezone(TIMEZONE))
        )

        for command in self.bot.commands:
            if command.hidden:
                embed.add_field(name=f".**{command.name}**", value=f" -> {command.help}" or "No description", inline=False)

        embed.set_footer(text=f"Sent by {ctx.author.name}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(OwnerHelp(bot))
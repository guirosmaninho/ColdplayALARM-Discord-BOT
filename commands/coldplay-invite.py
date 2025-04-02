import discord
from discord.ext import commands
import datetime
import pytz
import asyncio

TIMEZONE = "Europe/Lisbon"

class invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coldplay-invite")
    async def invite(self, ctx):
        """
        Returns the invite link for the bot.
        """
        embed = discord.Embed(
            title="I am ready to have a Adventure of a Lifetime in a new server!",
            description=f"To invite **{self.bot.user.name}** to your server click **[HERE](https://discord.com/oauth2/authorize?client_id=1353447377092218961&permissions=8&integration_type=0&scope=bot)**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(pytz.timezone(TIMEZONE))
        )
        embed.set_footer(text=f"Sent by {self.bot.user.name}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(invite(bot))
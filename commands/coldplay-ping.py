import discord
from discord.ext import commands
import datetime
import pytz
import asyncio

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coldplay-ping")
    async def ping(self, ctx):
        """
        Returns the latency of the bot.
        """
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title=":ping_pong: Pong!",
            description=f"My latency is currently **{latency}** ms.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"Sent by {self.bot.user.name}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))
import discord
from discord.ext import commands
import datetime
import pytz
import random
import main

TIMEZONE = "Europe/Lisbon"

class image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coldplay-image")
    async def invite(self, ctx):
        """
        Sends a random Coldplay image from the image folder.
        """
        embed = discord.Embed(
            title=f"{main.get_random_emoji()} Here's a random **Coldplay** image...",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(pytz.timezone(TIMEZONE))
        )
        random_image_number = random.randint(1, main.NUM_IMAGES)
        image_url = f"https://github.com/guirosmaninho/ColdplayALARM-Discord-BOT/blob/main/images/banner/coldplay{random_image_number}.jpeg?raw=true"
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Image ID: {random_image_number} | Sent by {self.bot.user.name}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        await ctx.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(image(bot))
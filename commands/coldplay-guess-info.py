import discord
from discord.ext import commands
import sqlite3

class GuessInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_top_songs(self):
        conn = sqlite3.connect('data/coldplay-songs.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, guesses, right_guesses, wrong_guesses,
                   (CAST(right_guesses AS FLOAT) / guesses) * 100 AS accuracy
            FROM lyrics
            WHERE guesses > 0
            ORDER BY accuracy DESC
            LIMIT 5
        ''')
        top_songs = cursor.fetchall()
        conn.close()
        return top_songs

    @commands.command(name="coldplay-guess-info")
    async def guess_info(self, ctx):
        """
        Displays the top 5 most rightly guessed Coldplay songs.
        """
        top_songs = self.get_top_songs()
        if not top_songs:
            await ctx.send("No songs found in the database.")
            return

        embed = discord.Embed(
            title="🎵 Top 5 Most Rightly Guessed Coldplay Songs 🎵",
            color=discord.Color.blue()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        for i, (name, guesses, right_guesses, wrong_guesses, accuracy) in enumerate(top_songs, start=1):
            embed.add_field(name=f"{i}. {name}", value=f"Stats: **{guesses}** guesses (**{round(accuracy, 2)}%**)", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GuessInfo(bot))
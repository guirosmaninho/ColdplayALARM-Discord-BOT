import discord
from discord.ext import commands
import random
import asyncio
import sqlite3

class ColdplayLyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_random_song_lyrics(self):
        conn = sqlite3.connect('data/coldplay-songs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, lyric, guesses, right_guesses, wrong_guesses FROM lyrics ORDER BY RANDOM() LIMIT 1')
        song = cursor.fetchone()
        conn.close()
        if song:
            name, lyrics, guesses, right_guesses, wrong_guesses = song
            lyrics_list = lyrics.split('\n')
            if len(lyrics_list) >= 2:
                start_index = random.randint(0, len(lyrics_list) - 2)
                return name, lyrics_list[start_index:start_index + 2], guesses, right_guesses, wrong_guesses
        return None, None, None, None, None

    @commands.command(name="coldplay-guess")
    async def guess_lyrics(self, ctx):
        """
        Sends two consecutive lines from a Coldplay song and asks the user to guess the song name.
        """
        song_name, lyrics, guesses, right_guesses, wrong_guesses = self.get_random_song_lyrics()
        if not song_name or not lyrics:
            await ctx.send("No lyrics found in the database.")
            return

        lyric1, lyric2 = lyrics

        embed = discord.Embed(
            title="🎵 Coldplay Lyrics Challenge 🎵",
            description=f"Guess the song name!\n\nSong Title accuracy: {round((right_guesses / guesses) * 100, 2) if guesses > 0 else 0}%",
            color=discord.Color.gold()
        )
        embed.add_field(name=lyric1, value=lyric2, inline=False)
        embed.set_footer(text="You have 20 seconds to answer!")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=20)
            conn = sqlite3.connect('data/coldplay-songs.db')
            cursor = conn.cursor()
            if msg.content.lower() == song_name.lower():
                cursor.execute('''
                UPDATE lyrics
                SET guesses = guesses + 1, right_guesses = right_guesses + 1
                WHERE name = ?
                ''', (song_name,))
                conn.commit()
                embed = discord.Embed(
                    title="✅ Correct!",
                    description=f"The song was **{song_name}** 🎶",
                    color=discord.Color.green()
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
            else:
                cursor.execute('''
                UPDATE lyrics
                SET guesses = guesses + 1, wrong_guesses = wrong_guesses + 1
                WHERE name = ?
                ''', (song_name,))
                conn.commit()
                embed = discord.Embed(
                    title="❌ Wrong!",
                    description=f"The correct answer was **{song_name}**.",
                    color=discord.Color.red()
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
            conn.close()
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏳ Time's up!",
                description=f"The song was **{song_name}**.",
                color=discord.Color.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ColdplayLyrics(bot))
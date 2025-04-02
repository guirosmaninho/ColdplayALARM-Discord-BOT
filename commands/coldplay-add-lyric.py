import discord
from discord.ext import commands
import sqlite3


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coldplay-add-lyric", hidden=True)
    @commands.is_owner()
    async def add_song(self, ctx, name: str, difficulty: int, *lyrics: str):
        """
        Adds a new song to the database. Only the bot owner can use this command.
        """
        lyrics_text = "\n".join(lyrics)

        # Connect to the SQLite database
        conn = sqlite3.connect('data/coldplay-songs.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS lyrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            difficulty INTEGER,
            guesses INTEGER DEFAULT 0,
            right_guesses INTEGER DEFAULT 0,
            wrong_guesses INTEGER DEFAULT 0,
            lyric TEXT
        )
        ''')

        # Insert the new song into the lyrics table
        cursor.execute('''
        INSERT INTO lyrics (name, difficulty, guesses, right_guesses, wrong_guesses, lyric)
        VALUES (?, ?, 0, 0, 0, ?)
        ''', (name, difficulty, lyrics_text))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        await ctx.send(f"Song '{name}' added to the database.")


async def setup(bot):
    await bot.add_cog(Music(bot))
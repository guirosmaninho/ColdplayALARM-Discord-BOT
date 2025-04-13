import sqlite3
import asyncio
from discord.ext import commands
from main import warning_message
from main import embed_message

class DeleteLyric(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coldplay-delete-lyric", hidden=True)
    @commands.is_owner()
    async def delete_lyric(self, ctx):
        """
        Deletes a lyric from the database by its ID.
        """
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        lyric_list = "No lyrics found in the database."

        try:
            conn = sqlite3.connect('data/coldplay-songs.db')
            cursor = conn.cursor()

            cursor.execute("SELECT id, name FROM lyrics ORDER BY id DESC LIMIT 3")
            lyrics = cursor.fetchall()

            if lyrics:
                lyric_list = "\n".join([f"ID: **{lyric[0]}**, Song Title: **{lyric[1]}**" for lyric in lyrics])

        except Exception as e:
            warning_message(3, ctx.channel, "An error occurred...")

        embed_message(ctx.channel, "DELETE LYRIC", f"Last 3 lyrics added to the database:\n{lyric_list}\n\nPlease provide the ID of the lyric you want to delete")

        try:
            msg = await ctx.bot.wait_for("message", check=check, timeout=60)
            lyric_id = msg.content.strip()

            conn = sqlite3.connect('data/coldplay-songs.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM lyrics WHERE id = ?", (lyric_id,))
            lyric = cursor.fetchone()

            if lyric:
                cursor.execute("DELETE FROM lyrics WHERE id = ?", (lyric_id,))
                conn.commit()
                warning_message(1, ctx.channel, f"Lyric with ID {lyric_id} has been successfully deleted.")
            else:
                warning_message(3, ctx.channel, f"No lyric found with ID {lyric_id}. Please try again.")

            conn.close()

        except asyncio.TimeoutError:
            warning_message(3, ctx.channel, "You took too long to respond. Please try again.")
        except Exception as e:
            warning_message(3, ctx.channel, f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(DeleteLyric(bot))
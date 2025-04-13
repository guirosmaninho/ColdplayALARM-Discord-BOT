import sqlite3
import asyncio
from discord.ext import commands
from main import warning_message, embed_message

class DeleteEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coldplay-delete-event", hidden=True)
    @commands.is_owner()
    async def delete_event(self, ctx):
        """
        Deletes an event from the database by its ID.
        """
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        embed_message(ctx.channel, "DELETE EVENT", "What type of event do you want to delete? (Options: `birthday`, `album`, `single`, `other`)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            event_type = msg.content.lower()
            if event_type not in ["birthday", "album", "single", "other"]:
                warning_message(3, ctx.channel, "Invalid type. Please restart the command.")
                return
        except asyncio.TimeoutError:
            warning_message(3, ctx.channel, "You took too long to respond. Please restart the command.")
            return

        event_list = "No events found in the database."
        try:
            conn = sqlite3.connect('data/coldplay-events.db')
            cursor = conn.cursor()

            cursor.execute(f"SELECT id, day, month, year FROM {event_type}s ORDER BY id DESC LIMIT 5")
            events = cursor.fetchall()

            if events:
                event_list = "\n".join([f"ID: **{event[0]}**, Date: **{event[1]}/{event[2]}/{event[3]}**" for event in events])

        except Exception as e:
            warning_message(3, ctx.channel, "An error occurred while fetching events.")
            return

        embed_message(ctx.channel, "DELETE EVENT", f"Last 5 {event_type} events:\n{event_list}\n\nPlease provide the ID of the event you want to delete.")

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            event_id = msg.content.strip()

            cursor.execute(f"SELECT * FROM {event_type}s WHERE id = ?", (event_id,))
            event = cursor.fetchone()

            if event:
                cursor.execute(f"DELETE FROM {event_type}s WHERE id = ?", (event_id,))
                conn.commit()
                warning_message(1, ctx.channel, f"Event with ID {event_id} has been successfully deleted.")
            else:
                warning_message(3, ctx.channel, f"No event found with ID {event_id}. Please try again.")

            conn.close()

        except asyncio.TimeoutError:
            warning_message(3, ctx.channel, "You took too long to respond. Please try again.")
        except Exception as e:
            warning_message(3, ctx.channel, "An error occurred...")

async def setup(bot):
    await bot.add_cog(DeleteEvent(bot))
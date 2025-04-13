import asyncio
from urllib.parse import urlparse
import discord
from discord.ext import commands
import sqlite3
from main import warning_message, embed_message

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coldplay-add-event", hidden=True)
    @commands.is_owner()
    async def add_event(self, ctx):
        """
        Adds an event to the database.
        """
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        embed_message(ctx.channel, "ADD EVENT", "What type of event is this? (Options: `birthday`, `album`, `single`, `other`)")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=180)
            event_type = msg.content.lower()
            if event_type not in ["birthday", "album", "single", "other"]:
                warning_message(3, ctx.channel, "Invalid type. Please restart the command.")
                return
        except asyncio.TimeoutError:
            warning_message(3, ctx.channel, "You took too long to respond. Please restart the command.")
            return

        day, month, year = await self.ask_for_date(ctx, check)
        if day is None:
            return

        conn = sqlite3.connect('data/coldplay-events.db')
        cursor = conn.cursor()

        if event_type == "birthday":
            cursor.execute('''CREATE TABLE IF NOT EXISTS birthdays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day INTEGER, month INTEGER, year INTEGER,
                name TEXT, role TEXT, image TEXT)''')

            name = await self.ask(ctx, check, "Enter the person's name:")
            if name is None: return
            role = await self.ask(ctx, check, "Enter the person's role:")
            if role is None: return
            image = await self.ask_url(ctx, check, "Enter the image link:")

            cursor.execute('''INSERT INTO birthdays (day, month, year, name, role, image)
                              VALUES (?, ?, ?, ?, ?, ?)''', (day, month, year, name, role, image))

        elif event_type == "single":
            cursor.execute('''CREATE TABLE IF NOT EXISTS singles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day INTEGER, month INTEGER, year INTEGER,
                single_name TEXT, album_name TEXT, image TEXT)''')

            single = await self.ask(ctx, check, "Enter the single name:")
            if single is None: return
            album = await self.ask(ctx, check, "Enter the album name:")
            if album is None: return
            image = await self.ask_url(ctx, check, "Enter the image link:")

            cursor.execute('''INSERT INTO singles (day, month, year, single_name, album_name, image)
                              VALUES (?, ?, ?, ?, ?, ?)''', (day, month, year, single, album, image))

        elif event_type == "album":
            cursor.execute('''CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day INTEGER, month INTEGER, year INTEGER,
                album_name TEXT, songs TEXT, image TEXT)''')

            album_name = await self.ask(ctx, check, "Enter the album name:")
            if album_name is None: return
            songs = await self.ask(ctx, check, "Enter all songs in the album (comma-separated):")
            if songs is None: return
            image = await self.ask_url(ctx, check, "Enter the image link:")

            cursor.execute('''INSERT INTO albums (day, month, year, album_name, songs, image)
                              VALUES (?, ?, ?, ?, ?, ?)''', (day, month, year, album_name, songs, image))

        elif event_type == "other":
            cursor.execute('''CREATE TABLE IF NOT EXISTS others (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day INTEGER, month INTEGER, year INTEGER,
                hour INTEGER, minute INTEGER,
                title TEXT, description TEXT, image TEXT)''')

            hour = await self.ask_optional_int(ctx, check, "Enter the hour (0-23) [write \"NA\" if not applicable]:")
            minute = await self.ask_optional_int(ctx, check, "Enter the minute (0-59) [write \"NA\" if not applicable]:")
            title = await self.ask(ctx, check, "Enter the title:")
            if title is None: return
            description = await self.ask(ctx, check, "Enter the description:")
            if description is None: return
            image = await self.ask_url(ctx, check, "Enter the image link [write \"NA\" if not applicable]:")

            cursor.execute('''INSERT INTO others (day, month, year, hour, minute, title, description, image)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (day, month, year, hour, minute, title, description, image))

        conn.commit()
        conn.close()

        warning_message(1, ctx.channel, f"Event of type '{event_type}' added successfully.")

    async def ask(self, ctx, check, prompt):
        embed_message(ctx.channel, "Add event", prompt)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            return msg.content.strip()
        except asyncio.TimeoutError:
            warning_message(3, ctx.channel, "Timeout. Please restart the command.")
            return None

    async def ask_url(self, ctx, check, prompt):
        embed_message(ctx.channel, "Add event", prompt)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            content = msg.content.strip()
            if content == "na":
                return None
            parsed = urlparse(content)
            if parsed.scheme in ["http", "https"] and parsed.netloc:
                return content
            warning_message(3, ctx.channel, "Invalid URL. Please restart.")
            return None
        except asyncio.TimeoutError:
            warning_message(3, ctx.channel, "Timeout. Please restart.")
            return None

    async def ask_optional_int(self, ctx, check, prompt):
        embed_message(ctx.channel, "Add event", prompt)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            if msg.content.strip().lower() == "na":
                return None
            return int(msg.content)
        except (ValueError, asyncio.TimeoutError):
            warning_message(3, ctx.channel, "Invalid number or timeout. Please restart.")
            return None

    async def ask_for_date(self, ctx, check):
        for field, limit in [("day", 31), ("month", 12), ("year", 9999)]:
            embed_message(ctx.channel, "ADD EVENT", f"**CONFIGURE DATE |** Enter the **{field.capitalize()}** [1-{limit}]:")
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
                value = int(msg.content)
                if field != "year" and not (1 <= value <= limit):
                    warning_message(3, ctx.channel, f"Invalid {field}. Please restart.")
                    return None, None, None
                if field == "day": day = value
                if field == "month": month = value
                if field == "year": year = value
            except (ValueError, asyncio.TimeoutError):
                warning_message(3, ctx.channel, f"Invalid or missing {field}. Please restart.")
                return None, None, None
        return day, month, year


async def setup(bot):
    await bot.add_cog(Event(bot))

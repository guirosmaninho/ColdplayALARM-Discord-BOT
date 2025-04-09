import asyncio
import datetime
import json
import os
import random
import sqlite3
import subprocess
import requests
from typing import Optional

import discord
import pytz
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv('super_secret_file_with_ABSOLUTELY_no_tokens.env')

# Configuration
TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNERID"))
TIMEZONE = "Europe/Lisbon"
CONCERT_FILE = "data/coldplay_concerts.json"
NUM_IMAGES = 0

repo_url = "https://api.github.com/repos/guirosmaninho/ColdplayALARM-Discord-BOT/contents/images/banner"
img_repo_url = "https://github.com/guirosmaninho/ColdplayALARM-Discord-BOT/blob/main/images/banner"
response = requests.get(repo_url)
if response.status_code == 200:
    contents = response.json()
    file_count = len(contents)

    if isinstance(file_count, int) and file_count > 0:
        NUM_IMAGES = file_count
    else:
        print("Error: No images found!")

# Initialize bot with proper intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix=".",
    intents=intents,
    activity=discord.Game(name="Having an Adventure of a Lifetime")
)

# Connect to the database
conn = sqlite3.connect('data/guild_settings.db')
c = conn.cursor()

# Ensure the table exists
c.execute('''CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id BIGINT PRIMARY KEY,
                daily_message_channel_id BIGINT
            )''')
conn.commit()

concert_data = []

async def update_concert_data():
    """
    Reads the concert data from the JSON file every 6 hours and stores it globally.
    """
    global concert_data
    while True:
        now = datetime.datetime.now(pytz.timezone(TIMEZONE))
        try:
            with open(CONCERT_FILE, "r", encoding='utf-8') as f:
                concert_data = json.load(f)
            print(f"Concert data updated at {now.hour}:{now.minute}:{now.second}.")
        except Exception as e:
            print(f"Error updating concert data: {e}")

        await asyncio.sleep(6*60*60)  # Wait for 6 hours before updating again


async def get_next_concert() -> discord.Embed:
    """
    Fetch the next Coldplay concert from the preloaded data.
    """
    global concert_data

    now = datetime.datetime.now(pytz.timezone(TIMEZONE)).date()

    for concert in concert_data:
        try:
            concert_date = datetime.datetime.strptime(concert["date"], "%d/%m/%Y").date()
            if concert_date >= now:
                embed = discord.Embed(
                    title="Next Coldplay Concert",
                    color=discord.Color(random.randint(0, 0xFFFFFF)),
                    timestamp=datetime.datetime.now(pytz.timezone(TIMEZONE))
                )
                embed.add_field(name="Stadium: ", value=concert['stadium'])
                embed.add_field(name="City: ", value=concert['city'])
                embed.add_field(name="Region: ", value=concert['region'])
                embed.add_field(name="Date: ", value=concert['date'])
                soldout_text = f"[{concert['soldout']}]({concert['link']})"
                embed.add_field(name="Sold out: ", value=soldout_text, inline=True)
                if NUM_IMAGES > 0:
                    random_image_number = random.randint(1, NUM_IMAGES)
                    image_url = f"{img_repo_url}/coldplay{random_image_number}.jpeg?raw=true"
                    embed.set_image(url=image_url)
                embed.set_footer(text=f"Sent by {bot.user.name}")
                return embed
        except (KeyError, ValueError):
            continue

    embed = discord.Embed(
        title="No Upcoming Concerts",
        description="No upcoming concerts found.",
        color=discord.Color.red()
    )
    return embed

def warning_message(severity, channel, message):
    colors = {1: discord.Color.green(), 2: discord.Color.orange(), 3: discord.Color.red()}
    embed = discord.Embed(
        title="Warning!",
        description=message,
        color = colors.get(severity, discord.Color.default()),
        timestamp=datetime.datetime.now(pytz.timezone(TIMEZONE))
    )
    embed.set_footer(text=f"Sent by {bot.user.name}")
    asyncio.ensure_future(channel.send(embed=embed))

    return 0

@bot.command(name="coldplay-setup")
@commands.has_permissions(administrator=True)
async def coldplay_setup(ctx, channel_id: Optional[int] = None):
    """
    Sets the channel for daily Coldplay messages.
    """
    if channel_id is None:
        warning_message(3, ctx.channel, "Please provide a channel ID. Usage: `.coldplay-setup [channel_id]`")
        return

    guild_id = ctx.guild.id

    # Check if the channel ID is valid
    channel = bot.get_channel(channel_id)
    if not channel:
        warning_message(3, ctx.channel, "Invalid channel ID. Please provide a valid channel ID.")
        return

    # Save the channel ID in the database
    c.execute('REPLACE INTO guild_settings (guild_id, daily_message_channel_id) VALUES (?, ?)', (guild_id, channel_id))
    conn.commit()

    warning_message(1, ctx.channel, f"Daily Coldplay message channel set to {channel.mention}")

@coldplay_setup.error
async def coldplay_setup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        warning_message(3, ctx.channel, "You do not have permission to use this command.")

async def send_daily_message():
    await bot.wait_until_ready()

    while not bot.is_closed():
        now = datetime.datetime.now(pytz.timezone(TIMEZONE))
        if now.hour == 0 and now.minute == 0:
            c.execute('SELECT guild_id, daily_message_channel_id FROM guild_settings')
            guild_settings = c.fetchall()

            for guild_id, channel_id in guild_settings:
                guild = bot.get_guild(guild_id)
                if guild:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        embed = None
                        for concert in concert_data:
                            concert_date = datetime.datetime.strptime(concert["date"], "%d/%m/%Y").date()
                            if concert_date == now.date():
                                embed = discord.Embed(
                                    title="🎉 Today is the Day! 🎶",
                                    description=f"Coldplay is performing today at **{concert['stadium']}**, {concert['city']}!",
                                    color=discord.Color.gold(),
                                    timestamp=now
                                )
                                embed.add_field(name="Region", value=concert['region'], inline=True)
                                embed.add_field(name="Soldout", value=concert['soldout'], inline=True)
                                embed.add_field(name="More Info", value=f"[Click Here]({concert['link']})", inline=False)
                                if NUM_IMAGES > 0:
                                    random_image_number = random.randint(1, NUM_IMAGES)
                                    image_url = f"{img_repo_url}/coldplay{random_image_number}.jpeg?raw=true"
                                    embed.set_image(url=image_url)
                                embed.set_footer(text=f"Sent by {bot.user.name}")
                                break

                        if not embed:
                            # Default message for non-concert days
                            embed = await get_next_concert()

                        try:
                            await channel.send(embed=embed)
                            print(f"Sent daily message at {now.hour}:{now.minute}:{now.second}")
                        except discord.errors.Forbidden:
                            print(f"Error: Bot lacks permission to send messages in {channel.name} of guild {guild.name}")

            await asyncio.sleep(60)  # Wait a minute to prevent duplicate sends
        await asyncio.sleep(30)  # Check every 30 seconds


@bot.command(name="coldplay-dates")
async def coldplay_dates(ctx):
    """
    Sends the next 4 Coldplay concerts from the preloaded data.
    """
    global concert_data

    if not concert_data:
        warning_message(2,ctx.channel,"No concerts found in the database.")
        return

    now = datetime.datetime.now(pytz.timezone(TIMEZONE))

    embed = discord.Embed(
        title="🌙✨ Next 4 Coldplay Concerts ☽ ☽ ☽ ◯ ☾ ☾ ☾",
        color=discord.Color(random.randint(0, 0xFFFFFF)),
        description = f"To view the all upcoming concerts, click [here](https://www.coldplay.com/tour/).",
        timestamp=now
    )

    upcoming_concerts = []
    for concert in concert_data:
        concert_date = datetime.datetime.strptime(concert["date"], "%d/%m/%Y")
        concert_date = pytz.timezone(TIMEZONE).localize(concert_date)
        if concert_date >= now:
            upcoming_concerts.append(concert)
        if len(upcoming_concerts) >= 5:
            break

    for concert in upcoming_concerts[:4]:
        concert_date = datetime.datetime.strptime(concert["date"], "%d/%m/%Y")
        concert_date = pytz.timezone(TIMEZONE).localize(concert_date)
        time_left = concert_date - now
        days_left = time_left.days

        embed.add_field(name="Stadium", value=concert['stadium'], inline=False)
        embed.add_field(name="City", value=concert['city'], inline=True)
        embed.add_field(name="Region: ", value=concert['region'], inline=True)
        embed.add_field(name="Date", value=f"{concert['date']} ({days_left} days left)", inline=True)
        embed.add_field(name="Soldout: ", value=concert['soldout'], inline=True)
        moreinfo_text = f"[CLICK HERE]({concert['link']})"
        embed.add_field(name="More info: ", value=moreinfo_text, inline=True)
        if NUM_IMAGES > 0:
            random_image_number = random.randint(1, NUM_IMAGES)
            image_url = f"{img_repo_url}/coldplay{random_image_number}.jpeg?raw=true"
            embed.set_image(url=image_url)
        embed.set_footer(text=f"Sent by {bot.user.name}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

@bot.command(name="coldplay-update", hidden=True)
async def update_db(ctx):
    """
    Runs the updatedb.py file to update the database and reloads the concert data.
    """
    if ctx.author.id != OWNER_ID:
        warning_message(3, ctx.channel, "You do not have permission to use this command.")
        return

    try:
        result = subprocess.run(["python3", "data/updatedb.py"], capture_output=True, text=True)
        if result.returncode == 0:
            await update_concert_data()  # Reload concert data
            warning_message(1, ctx.channel, "Database updated and concert data reloaded successfully.")
            print("Updated DB and reloaded concert data")
        else:
            warning_message(3, ctx.channel, f"Error updating database: {result.stderr}")
    except Exception as e:
        warning_message(3, ctx.channel, f"Unexpected error running update: {str(e)}")

async def load_cogs():
    for filename in os.listdir("./commands"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"commands.{filename[:-3]}")  # Remove .py from filename
                print(f"Loaded {filename}")
            except commands.errors.ExtensionAlreadyLoaded:
                print(f"Extension {filename} is already loaded.")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

def get_random_emoji():
    emojis = ["🌙", "⭐", "🕰️", "🪐", "❤️‍🔥", "🎹", "🎵🔭", "🎸🔥", "👁️💫", "⏳💔", "🌍✨", "✊🌈"]
    return random.choice(emojis)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(update_concert_data())
    bot.loop.create_task(send_daily_message())

if __name__ == "__main__":
    asyncio.run(load_cogs())  # Load cogs first
    bot.run(TOKEN)  # Then start bot
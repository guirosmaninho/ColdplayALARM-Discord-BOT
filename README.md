![Picture taken during Coldplay's concert in Coimbra, Portugal. 2023](https://github.com/guirosmaninho/ColdplayALARM-Discord-BOT/blob/main/images/banner/coldplay47.jpeg?raw=true)

# 🎶 Overview - Coldplay ALARM Discord BOT
$${\color{red} ATENTION : \space THIS \space BOT \space IS \space STILL \space UNDER \space DEVELOPEMENT}$$

Coldplay ALARM is a fan-made Discord BOT, developed in Python, designed to bring joy to all Coldplay lovers by providing updates, mini-games, and content inspired by the band. Whether you’re waiting for the next tour date or testing your Coldplay lyric knowledge, this bot has something for every (super)fan.

# 🛠️ Features 

|      Commands  |Description                          |
|----------------|-------------------------------|
|.coldplay-dates|`Get info about the next 4 Coldplay Concerts.`            |
|.coldplay-guess          |`Play a game: guess the song name based on two lines of lyrics.`            |
|.coldplay-guess-info          |`Gives you stats about the most guessed songs.`            |
|.coldplay-image          |`Sends a random Coldplay image.`|
|.coldplay-invite          |`Sends the invite link to add the Bot to your own server.`|
|.coldplay-help          |`Displays all available commands and how to use them.`|
|.coldplay-ping          |`Returns the latency of the bot.`|


# Getting Started
## 1. Clone the repository
``` bash
git clone https://github.com/guirosmaninho/ColdplayALARM-Discord-BOT.git
cd ColdplayALARM-Discord-BOT
```

## 2. Install dependencies
Make sure you have Python 3.10+ and install all required packages:
``` bash
pip install -r requirements.txt
```

## 3. Setup your .env file
Create a .env filein the root directory with the name **super_secret_file_with_ABSOLUTELY_no_tokens.env** and add your bot token and user id:
``` env
TOKEN=your_token_here
OWNERID=your_user_id_here
```

## 4. Run the bot
``` bash
python main.py
```

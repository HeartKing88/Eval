from Bad import app
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Config import mongo
from pymongo import ASCENDING
import json
from datetime import datetime, timedelta

# MongoDB collections
games = mongo["wordgame"]["games"]
scores = mongo["wordgame"]["scores"]

# Load valid words from words.json
with open("Bad/Modules/words.json") as f:
    VALID_WORDS = set(json.load(f))  # Ensure words.json is a JSON array of words

# Active games structure: {chat_id: {"players": [user1, user2], "words": {user1: [], user2: []}}}
active_games = {}

@app.on_message(filters.command("play") & filters.group)
async def play_handler(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in active_games:
        # Create a new game and wait for a second player
        active_games[chat_id] = {"players": [user_id], "words": {user_id: []}}
        join_button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Game", callback_data=f"join_game_{chat_id}")]]
        )
        await message.reply(
            f"Game started by {message.from_user.mention}. Waiting for a 2nd player...",
            reply_markup=join_button
        )
    else:
        await message.reply("Game already in progress.")

@app.on_callback_query(filters.regex(r"join_game_(\d+)"))
async def join_game_handler(_, query):
    chat_id = int(query.data.split("_")[-1])
    user_id = query.from_user.id

    if chat_id in active_games and len(active_games[chat_id]["players"]) == 1:
        # Add the second player to the game
        active_games[chat_id]["players"].append(user_id)
        active_games[chat_id]["words"][user_id] = []
        await query.answer("You joined the game!")
        await query.message.edit_text(
            f"{query.from_user.mention} joined the game!\nStart typing 5-letter words. First to 10 wins 25 points."
        )
    else:
        await query.answer("Unable to join the game.", show_alert=True)

@app.on_message(filters.text & filters.group)
async def word_handler(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    word = message.text.lower()

    if chat_id not in active_games:
        return

    game = active_games[chat_id]
    if user_id not in game["players"]:
        return

    # Validate the word
    if len(word) != 5:
        await message.reply(f"❌ '{word}' is not a 5-letter word!")
        return

    if word not in VALID_WORDS:
        await message.reply(f"❌ '{word}' is not a valid word!")
        return

    if any(word in game["words"][p] for p in game["players"]):
        await message.reply("❌ This word has already been used!")
        return

    # Add word to the player's list
    game["words"][user_id].append(word)
    await message.reply(f"✅ '{word}' is valid!")

    # Check if the player has won
    if len(game["words"][user_id]) == 10:
        await message.reply(f"{message.from_user.mention} wins and earns 25 points!")
        await update_score(user_id)
        del active_games[chat_id]

@app.on_message(filters.command("endgame") & filters.group)
async def end_game_handler(_, message: Message):
    chat_id = message.chat.id

    if chat_id in active_games:
        del active_games[chat_id]
        await message.reply("The game has been ended!")
    else:
        await message.reply("No active game found in this chat.")

async def update_score(user_id):
    scores.update_one(
        {"user_id": user_id},
        {"$inc": {"score": 25}},
        upsert=True
    )

@app.on_message(filters.command("leaderboard"))
async def global_leaderboard(_, message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Today", callback_data="leaderboard_today"),
         InlineKeyboardButton("This Week", callback_data="leaderboard_week")],
        [InlineKeyboardButton("This Month", callback_data="leaderboard_month"),
         InlineKeyboardButton("This Year", callback_data="leaderboard_year")],
        [InlineKeyboardButton("All Time", callback_data="leaderboard_all")]
    ])
    await message.reply("Choose a leaderboard filter:", reply_markup=buttons)

@app.on_callback_query(filters.regex(r"leaderboard_(\w+)"))
async def leaderboard_handler(_, query):
    time_filter = query.data.split("_")[-1]
    now = datetime.utcnow()

    if time_filter == "today":
        start_time = now - timedelta(days=1)
    elif time_filter == "week":
        start_time = now - timedelta(weeks=1)
    elif time_filter == "month":
        start_time = now - timedelta(days=30)
    elif time_filter == "year":
        start_time = now - timedelta(days=365)
    else:  # "all"
        start_time = None

    if start_time:
        top = scores.find({"last_updated": {"$gte": start_time}}).sort("score", -1).limit(10)
    else:
        top = scores.find().sort("score", -1).limit(10)

    text = f"**{time_filter.capitalize()} Leaderboard**\n\n"
    for i, x in enumerate(top, 1):
        user = await app.get_users(x["user_id"])
        text += f"{i}. {user.mention} - {x['score']} pts\n"
    await query.message.edit_text(text)

@app.on_message(filters.command("myscore"))
async def myscore(_, message: Message):
    user_id = message.from_user.id
    data = scores.find_one({"user_id": user_id})
    points = data["score"] if data else 0
    await message.reply(f"Your score: {points} points")

@app.on_message(filters.command("help"))
async def help_handler(_, message: Message):
    await message.reply(
        "**Word Game Help**\n\n"
        "/play - Start a 2-player word game\n"
        "/leaderboard - Global leaderboard with filters\n"
        "/endgame - End the current game\n"
        "/myscore - Show your total score\n\n"
        "Game Rules:\n"
        "- Type valid 5-letter words\n"
        "- First to enter 10 valid words wins 25 points\n"
        "- No repeating words!\n"
        "- Valid words will show ✅, invalid words will show ❌"
    )

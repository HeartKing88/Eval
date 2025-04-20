from Bad import app
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Config import mongo
from pymongo import ASCENDING
import random

games = mongo["wordgame"]["games"]
scores = mongo["wordgame"]["scores"]

with open("Bad.Modules.words.json") as f:
    VALID_WORDS = set(f.read().splitlines())

# Active games structure: {chat_id: {"players": [user1, user2], "words": {user1: [], user2: []}}}
active_games = {}

@app.on_message(filters.command("play") & filters.group)
async def play_handler(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in active_games:
        active_games[chat_id] = {"players": [user_id], "words": {user_id: []}}
        await message.reply(f"Game started by {message.from_user.mention}. Waiting for 2nd player...")
    elif len(active_games[chat_id]["players"]) == 1 and user_id != active_games[chat_id]["players"][0]:
        active_games[chat_id]["players"].append(user_id)
        active_games[chat_id]["words"][user_id] = []
        await message.reply(f"{message.from_user.mention} joined the game!\nStart typing 5-letter words. First to 10 wins 25 points.")
    else:
        await message.reply("Game already in progress or you're already playing.")

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

    if len(word) != 5 or word not in VALID_WORDS:
        return

    if any(word in game["words"][p] for p in game["players"]):
        await message.reply("This word has already been used!")
        return

    game["words"][user_id].append(word)

    if len(game["words"][user_id]) == 10:
        await message.reply(f"{message.from_user.mention} wins and earns 25 points!")
        await update_score(user_id)
        del active_games[chat_id]

async def update_score(user_id):
    scores.update_one(
        {"user_id": user_id},
        {"$inc": {"score": 25}},
        upsert=True
    )

@app.on_message(filters.command("leaderboard"))
async def global_leaderboard(_, message: Message):
    top = scores.find().sort("score", -1).limit(10)
    text = "**Global Leaderboard**\n\n"
    for i, x in enumerate(top, 1):
        user = await app.get_users(x["user_id"])
        text += f"{i}. {user.mention} - {x['score']} pts\n"
    await message.reply(text)

@app.on_message(filters.command("groupleaderboard") & filters.group)
async def group_leaderboard(_, message: Message):
    chat_members = await app.get_chat_members(message.chat.id)
    member_ids = [m.user.id for m in chat_members if not m.user.is_bot]
    top = scores.find({"user_id": {"$in": member_ids}}).sort("score", -1).limit(10)

    text = "**Group Leaderboard**\n\n"
    for i, x in enumerate(top, 1):
        user = await app.get_users(x["user_id"])
        text += f"{i}. {user.mention} - {x['score']} pts\n"
    await message.reply(text)

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
        "/leaderboard - Global leaderboard\n"
        "/groupleaderboard - Group-only leaderboard\n"
        "/myscore - Show your total score\n\n"
        "Game Rules:\n"
        "- Type valid 5-letter words\n"
        "- First to enter 10 valid words wins 25 points\n"
        "- No repeating words!"
                      )

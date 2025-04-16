from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
import random
from Bad import app
from Config import MONGO_URL
import os
import json
import os

# Load words directly from words.json
WORDS_FILE_PATH = os.path.join(os.path.dirname(__file__), "words.json")  # Specify the correct file name
with open(WORDS_FILE_PATH, "r") as file:
    WORDS = json.load(file)


# MongoDB setup
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["wordseek_bot"]
games_col = db["games"]
scores_col = db["scores"]

def get_hint(secret, guess):
    result = ""
    for i in range(5):
        if guess[i] == secret[i]:
            result += "🟩 "
        elif guess[i] in secret:
            result += "🟨 "
        else:
            result += "🟥 "
    return result.strip()

@app.on_message(filters.command("new"))
async def new_game(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if a game is already active for this user/group
    existing_game = games_col.find_one({"chat_id": chat_id, "user_id": user_id, "active": True})
    if existing_game:
        return await message.reply("You already have an active game! Finish it before starting a new one.")

    # Only admins can start a game in groups
    if message.chat.type in ["group", "supergroup"]:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in ("administrator", "creator"):
            return await message.reply("Only admins can start a new game in this group.")

    word = random.choice(WORDS)
    games_col.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"word": word, "guesses": [], "active": True, "max_points": 30}},
        upsert=True
    )
    await message.reply(
        "Game started! Guess the 5-letter word! Your guess must be a 5-letter word composed of letters only!"
    )

@app.on_message(filters.text & ~filters.command(["new", "leaderboard", "myscore", "end"]))
async def handle_guess(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_input = message.text.strip().lower()

    # Fetch the game for the specific user/group
    game = games_col.find_one({"chat_id": chat_id, "user_id": user_id, "active": True})
    if not game:
        return  # No active game for this user/group

    # Validate if the input is 5 letters and alphabetical
    if len(user_input) != 5 or not user_input.isalpha():
        return  # Skip replying to avoid spam

    # Validate if the word is in the predefined word list
    if user_input not in WORDS:
        return await message.reply(f"`{user_input.upper()}` is not a valid word!")

    # Check if the word has already been guessed
    guesses = game.get("guesses", [])
    if any(guess["guess"] == user_input for guess in guesses):
        return await message.reply("Someone has already guessed your word. Please try another one!")

    correct_word = game["word"]
    hint = get_hint(correct_word, user_input)

    guesses.append({
        "user_id": user_id,
        "guess": user_input,
        "hint": hint
    })

    if user_input == correct_word:
        points_earned = max(0, game["max_points"] - len(guesses))
        scores_col.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {
                "$inc": {"score": points_earned},
                "$setOnInsert": {
                    "username": message.from_user.username or "",
                    "name": message.from_user.first_name
                }
            },
            upsert=True
        )
        games_col.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"active": False}})
        board = "\n".join([f"{g['hint']} `{g['guess'].upper()}`" for g in guesses])
        return await message.reply(
            f"{board}\n\n**{message.from_user.first_name}** guessed it correctly! The word was **{correct_word.upper()}**.\n"
            f"Added {points_earned} to the leaderboard.\nStart a new game with /new."
        )

    if len(guesses) >= 30:
        games_col.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"active": False}})
        board = "\n".join([f"{g['hint']} `{g['guess'].upper()}`" for g in guesses])
        return await message.reply(f"{board}\n\nGame over! The correct word was **{correct_word.upper()}**.")

    games_col.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"guesses": guesses}})
    board = "\n".join([f"{g['hint']} `{g['guess'].upper()}`" for g in guesses])
    await message.reply(board)

@app.on_message(filters.command("end"))
async def end_game(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Fetch the current game
    game = games_col.find_one({"chat_id": chat_id, "user_id": user_id, "active": True})
    if not game:
        return await message.reply("No active game to end.")

    games_col.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"active": False}})
    await message.reply("Your game has been ended. No score was awarded.")

@app.on_message(filters.command("leaderboard"))
async def leaderboard(client, message: Message):
    chat_id = message.chat.id
    top = list(scores_col.find({"chat_id": chat_id}).sort("score", -1).limit(10))
    if not top:
        return await message.reply("No scores yet!")

    text = "**🏆 Leaderboard:**\n"
    for i, user in enumerate(top, 1):
        name = user.get("name") or "Unknown"
        score = user.get("score", 0)
        text += f"{i}. {name} — {score} point(s)\n"

    await message.reply(text)

@app.on_message(filters.command("myscore"))
async def myscore(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    entry = scores_col.find_one({"user_id": user_id, "chat_id": chat_id})

    score = entry.get("score", 0) if entry else 0
    await message.reply(f"**Your score:** {score} point(s).")

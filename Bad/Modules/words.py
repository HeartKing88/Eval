from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
import random
from Bad import app
from Config import MONGO_URL

# Word list (5-letter words)
WORDS = ["apple", "grape", "peach", "mango", "lemon", "berry", "melon", "olive", "guava", "plums", "crown", "flips", "south", "house", "mouse"]

# MongoDB setup
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["wordseek_bot"]
games_col = db["games"]
scores_col = db["scores"]

def get_hint(secret, guess):
    result = ""
    for i in range(5):
        if guess[i] == secret[i]:
            result += "🟩"
        elif guess[i] in secret:
            result += "🟨"
        else:
            result += "🟥"
    return result

@app.on_message(filters.command("new"))
async def new_game(client, message: Message):
    chat_id = message.chat.id
    if message.chat.type in ["group", "supergroup"]:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in ("administrator", "creator"):
            return await message.reply("Only admins can start a new game.")

    word = random.choice(WORDS)
    games_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"word": word, "guesses": [], "active": True, "max_points": 30}},
        upsert=True
    )
    await message.reply("Game started! Guess the 5-letter word!")

@app.on_message(filters.text & ~filters.command)
async def handle_guess(client, message: Message):
    chat_id = message.chat.id
    user_input = message.text.strip().lower()

    if len(user_input) != 5 or not user_input.isalpha():
        return  # Ignore non-5-letter text inputs

    game = games_col.find_one({"chat_id": chat_id})
    if not game or not game.get("active"):
        return  # Ignore inputs when no active game exists

    correct_word = game["word"]
    guesses = game.get("guesses", [])
    hint = get_hint(correct_word, user_input)
    guesses.append({"user_id": message.from_user.id, "guess": user_input})

    if user_input == correct_word:
        user_id = message.from_user.id
        points_earned = max(0, game["max_points"] - len(guesses))
        scores_col.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {
                "$inc": {"score": points_earned},
                "$setOnInsert": {"username": message.from_user.username or "", "name": message.from_user.first_name}
            },
            upsert=True
        )
        games_col.update_one({"chat_id": chat_id}, {"$set": {"active": False}})
        return await message.reply(
            f"{hint}\n\n**{message.from_user.first_name}** guessed it correctly! The word was **{correct_word}**.\n"
            f"Added {points_earned} to the leaderboard.\nStart a new game with /new."
        )

    if len(guesses) >= 30:
        games_col.update_one({"chat_id": chat_id}, {"$set": {"active": False}})
        return await message.reply(f"{hint}\n\nGame over! The correct word was **{correct_word}**.")

    games_col.update_one({"chat_id": chat_id}, {"$set": {"guesses": guesses}})
    await message.reply(hint)

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

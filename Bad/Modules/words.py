from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
import random
import datetime
from Bad import app
from Config import MONGO_URL

# Word list (5-letter words)
WORDS = ["apple", "grape", "peach", "mango", "lemon", "berry", "melon", "olive", "guava", "plums"]

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


@app.on_message(filters.command("startt"))
async def start(client, message: Message):
    await message.reply_text(
        "**WordSeek**\nA fun and competitive Wordle-style game that you can play directly on Telegram!\n\n"
        "1. Use /new to start a game. Add me to a group with admin permission to play with your friends.\n"
        "2. Use /helpp to get help on how to play and commands list.\n\n"
        "🛠 Developed by You"
    )


@app.on_message(filters.command("helpp"))
async def help_command(client, message: Message):
    await message.reply_text(
        "**How to Play:**\n"
        "1. You have to guess a random 5-letter word.\n"
        "2. After each guess, you'll get hints:\n"
        "   🟩 - Correct letter in the right spot.\n"
        "   🟨 - Correct letter in the wrong spot.\n"
        "   🟥 - Letter not in the word.\n"
        "3. The game ends when someone guesses the word or after 30 guesses.\n\n"
        "**Commands:**\n"
        "/new - Start a new game.\n"
        "/end - End current game (admin only).\n"
        "/guess <word> - Make a guess.\n"
        "/leaderboard - Group leaderboard.\n"
        "/myscore - Your score."
    )


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
        {"$set": {"word": word, "guesses": [], "active": True}},
        upsert=True
    )
    await message.reply("A new game has started! Use `/guess <word>` to play.")


@app.on_message(filters.command("end"))
async def end_game(client, message: Message):
    chat_id = message.chat.id
    if message.chat.type in ["group", "supergroup"]:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in ("administrator", "creator"):
            return await message.reply("Only admins can end the game.")

    games_col.update_one({"chat_id": chat_id}, {"$set": {"active": False}})
    await message.reply("The current game has been ended.")


@app.on_message(filters.command("guess"))
async def guess_word(client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply("Usage: `/guess <5-letter word>`")

    guess = message.command[1].lower()
    if len(guess) != 5:
        return await message.reply("Please guess a valid 5-letter word.")

    game = games_col.find_one({"chat_id": chat_id})
    if not game or not game.get("active"):
        return await message.reply("No active game. Start one with /new.")

    correct_word = game["word"]
    guesses = game.get("guesses", [])
    hint = get_hint(correct_word, guess)
    guesses.append({"user_id": message.from_user.id, "guess": guess})

    if guess == correct_word:
        user_id = message.from_user.id
        scores_col.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {"$inc": {"score": 1}, "$setOnInsert": {"username": message.from_user.username or "", "name": message.from_user.first_name}},
            upsert=True
        )
        games_col.update_one({"chat_id": chat_id}, {"$set": {"active": False}})
        return await message.reply(f"{hint}\n\n**{message.from_user.first_name}** guessed it right! The word was **{correct_word}**.")

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


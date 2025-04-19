import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Bad import app
from Config import scores_col

games = {}
words_list = ["apple", "table", "grape", "brush", "plant", "sweet", "tears", "chair", "brick", "glass"]

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("Welcome to **Fastest Finger Duel**!\nUse /play to start 1v1 game.\nCheck /leaderboard to see scores.\nFor more commands, use /help.")

@app.on_message(filters.command("help"))
async def help_command(_, message: Message):
    await message.reply(
        "**Fastest Finger Duel Help**\n\n"
        "Commands:\n"
        "/start - Start the bot and get welcome message.\n"
        "/play - Join a game or start a new one.\n"
        "/leaderboard - View group or global leaderboard.\n"
        "/myscore - Check your group and global scores.\n"
        "/help - Show this help message.\n\n"
        "How to play:\n"
        "1. Use /play to join a game.\n"
        "2. Guess the correct word from the jumbled letters.\n"
        "3. Be the first to guess correctly and win points!"
    )

@app.on_message(filters.command("play"))
async def play(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in games:
        games[chat_id] = {
            "players": [user_id],
            "scores": {},
            "round": 0,
            "current_word": None,
            "active": False,
            "guesses": []  # To store guesses and their results
        }
        await message.reply("Waiting for opponent... Ask your friend to /play too.")
    else:
        if user_id in games[chat_id]["players"]:
            await message.reply("You are already in the game.")
            return

        games[chat_id]["players"].append(user_id)
        games[chat_id]["scores"] = {uid: 0 for uid in games[chat_id]["players"]}
        games[chat_id]["active"] = True
        await message.reply("Game started between 2 players! First to 5 rounds wins.")
        await run_game(chat_id)

async def run_game(chat_id):
    for round_no in range(5):
        word = random.choice(words_list)
        jumbled = "".join(random.sample(word, len(word)))
        games[chat_id]["current_word"] = word
        games[chat_id]["round"] += 1
        games[chat_id]["guesses"] = []  # Reset guesses for new round

        await app.send_message(chat_id, f"**Round {round_no + 1}**\nGuess the word: `{jumbled}`")

        try:
            winner_id = await wait_for_answer(chat_id, word)
            games[chat_id]["scores"][winner_id] += 1
            user = await app.get_users(winner_id)
            await app.send_message(chat_id, f"✅ Correct! {user.first_name} gets the point.")

            # Update scores
            scores_col.update_one(
                {"user_id": winner_id, "chat_id": chat_id},
                {"$inc": {"score": 1}, "$set": {"username": user.username, "name": user.first_name}},
                upsert=True
            )
            scores_col.update_one(
                {"user_id": winner_id, "chat_id": "global"},
                {"$inc": {"score": 1}, "$set": {"username": user.username, "name": user.first_name}},
                upsert=True
            )
        except asyncio.TimeoutError:
            await app.send_message(chat_id, f"⏰ Time's up! The word was **{word}**.")
        await asyncio.sleep(2)

    scores = games[chat_id]["scores"]
    winner_id = max(scores, key=scores.get)
    winner = await app.get_users(winner_id)
    result = "\n".join([f"{(await app.get_users(uid)).first_name}: {sc}" for uid, sc in scores.items()])
    await app.send_message(chat_id, f"🏁 **Game Over!**\n\n**Scores:**\n{result}\n\n**Winner:** {winner.first_name}")
    del games[chat_id]

async def wait_for_answer(chat_id, correct_word):
    future = asyncio.Future()

    def calculate_feedback(guess, correct_word):
        """Calculate the feedback for the guessed word."""
        feedback = []
        for i, char in enumerate(guess):
            if i < len(correct_word) and char == correct_word[i]:
                feedback.append("🟩")  # Correct letter and position
            elif char in correct_word:
                feedback.append("🟨")  # Correct letter but wrong position
            else:
                feedback.append("🟥")  # Incorrect letter
        return "".join(feedback)

    def checker(_, message: Message):
        if not games.get(chat_id) or not games[chat_id]["active"]:
            return
        if message.from_user.id not in games[chat_id]["players"]:
            return

        guess = message.text.lower()
        feedback = calculate_feedback(guess, correct_word)
        games[chat_id]["guesses"].append((message.from_user.first_name, feedback, guess))

        # Display all guesses so far
        guesses_text = "\n".join(
            [f"{player}: {feedback} `{guessed_word}`" for player, feedback, guessed_word in games[chat_id]["guesses"]]
        )
        app.send_message(chat_id, f"**Guesses so far:**\n{guesses_text}")

        if guess == correct_word:
            if not future.done():
                future.set_result(message.from_user.id)

    # Add the handler dynamically
    message_handler = app.add_handler(filters.text & filters.chat(chat_id), checker)

    try:
        return await asyncio.wait_for(future, timeout=15)
    finally:
        # Remove the handler after the round ends
        app.remove_handler(message_handler)

@app.on_message(filters.command("leaderboard"))
async def leaderboard(_, message: Message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏆 Group", callback_data="group_lb"),
            InlineKeyboardButton("🌍 Global", callback_data="global_lb")
        ]
    ])
    await message.reply("Choose leaderboard type:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^(group_lb|global_lb)$"))
async def show_lb(_, query):
    chat_id = query.message.chat.id
    mode = query.data
    text = ""

    if mode == "group_lb":
        top = scores_col.find({"chat_id": chat_id}).sort("score", -1).limit(10)
        text = "**🏆 Group Leaderboard:**\n"
    else:
        top = scores_col.find({"chat_id": "global"}).sort("score", -1).limit(10)
        text = "**🌍 Global Leaderboard:**\n"

    for i, user in enumerate(top, start=1):
        text += f"{i}. {user['name']} - {user['score']} pts\n"

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏆 Group", callback_data="group_lb"),
            InlineKeyboardButton("🌍 Global", callback_data="global_lb")
        ]
    ]))

@app.on_message(filters.command("myscore"))
async def myscore(_, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    group_data = scores_col.find_one({"user_id": user_id, "chat_id": chat_id})
    global_data = scores_col.find_one({"user_id": user_id, "chat_id": "global"})

    group_score = group_data["score"] if group_data else 0
    global_score = global_data["score"] if global_data else 0

    await message.reply(
        f"**Your Score:**\n\n"
        f"🏠 Group Score: {group_score} pts\n"
        f"🌍 Global Score: {global_score} pts"
)

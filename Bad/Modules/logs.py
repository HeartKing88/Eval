import asyncio
import os
import socket
from pyrogram import filters
from Bad import app, Bad

async def is_heroku():
    return "heroku" in socket.getfqdn()

@app.on_message(filters.command(["getlog", "logs", "getlogs"]))
async def log_(client, message):
    log_file = "log.txt"
    if os.path.exists(log_file):
        try:
            await message.reply_document(document=log_file)
        except Exception as e:
            await message.reply_text(f"An error occurred while sending the log file: {str(e)}")
    else:
        await message.reply_text("Log file does not exist.")

@app.on_message(filters.command(["cleanlogs"]))
async def clean_logs(client, message):
    log_file = "log.txt"
    try:
        with open(log_file, "w") as file:
            file.write("")  # Clear the content of the log file
        await message.reply_text("Old logs have been cleaned. New logs will be created.")
    except Exception as e:
        await message.reply_text(f"An error occurred while cleaning the log file: {str(e)}")

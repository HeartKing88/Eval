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
      

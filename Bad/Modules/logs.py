import asyncio
import os
import socket
import aiohttp
from pyrogram import filters
from Bad import app

BASE = "https://batbin.me/"

async def is_heroku():
    return "heroku" in socket.getfqdn()

async def post(url: str, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, *args, **kwargs) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
        return data

async def BadBin(text):
    resp = await post(f"{BASE}api/v2/paste", data={"text": text})
    if not resp["success"]:
        return
    link = BASE + resp["message"]
    return link

@app.on_message(filters.command(["getlog", "logs", "getlogs"]))
async def log_(client, message):
    log_file = "log.txt"
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                log_content = f.read()
            link = await BadBin(log_content)
            await message.reply_text(f"Log file uploaded to: {link}")
        except Exception as e:
            await message.reply_text(f"An error occurred while uploading the log file: {str(e)}")
    else:
        await message.reply_text("Log file does not exist.")

@app.on_message(filters.command(["clean"]))
async def clean_logs(client, message):
    log_file = "log.txt"
    if os.path.exists(log_file):
        try:
            with open(log_file, "w") as f:
                f.write("")
            await message.reply_text("Log file has been cleaned.")
        except Exception as e:
            await message.reply_text(f"An error occurred while cleaning the log file: {str(e)}")
    else:
        await message.reply_text("Log file does not exist.")

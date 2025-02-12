from pyrogram import Client
from telethon import TelegramClient
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import Config

# Pyrogram Client
app = Client(
    name="app",
    api_id=Config.APP_ID,
    api_hash=Config.HASH_ID,
    bot_token=Config.TOKEN,
    plugins=dict(root="Bad.Modules")
)

# Telethon Bot
Bad = TelegramClient(
    session="Bad",  # Add a session name here
    api_id=Config.APP_ID,
    api_hash=Config.HASH_ID
).start(bot_token=Config.TOKEN)

# Telegram (python-telegram-bot) Client
telegram_bot = Application.builder().token(Config.TOKEN).build()


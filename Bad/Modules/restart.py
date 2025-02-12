import os
import logging
from Bad import app
from pyrogram import filters, Client as PyroClient
from pyrogram.types import Message

# Initialize logger
logger = logging.getLogger(__name__)

@app.on_message(filters.command("rs") & ~filters.forwarded & ~filters.via_bot)
async def restart(client: PyroClient, message: Message):
    reply = await message.reply_text("**🔁 Restarting...**")
    await message.delete()
    await reply.edit_text("Successfully Restarted\nPlease wait 1-2 min for loading user plugins...")
    logger.info("Bot is restarting...")
    os.system(f"kill -9 {os.getpid()} && python3 -m Bad")
  

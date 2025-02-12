from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Bad import app

@app.on_message(filters.command("help") & ~filters.forwarded & ~filters.via_bot)
async def help_command(client, message):
    # Help command message delete karne ke liye
    await message.delete()

    text = """Wᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ʙᴏᴛ! Bᴇʟᴏᴡ ʏᴏᴜ ᴡɪʟʟ ғɪɴᴅ ᴀ ʟɪsᴛ ᴏғ ᴄᴏᴍᴍᴀɴᴅs ʏᴏᴜ ᴄᴀɴ ᴜsᴇ, ᴀʟᴏɴɢ ᴡɪᴛʜ ᴇxᴘʟᴀɴᴀᴛɪᴏɴs ᴀɴᴅ ᴇxᴀᴍᴘʟᴇs ғᴏʀ ᴇᴀᴄʜ.

/eval [expression] ➕: Evaluate a mathematical expression or code snippet.
/sh [command] 💻: Execute a shell command and return its output.
/install [package_name] 📦: Install a specified package or software.
/rs 🔄: Restart the bot or service."""

    await message.reply_text(text)

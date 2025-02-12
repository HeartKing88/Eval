from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@app.on_message(filters.command("start") & ~filters.forwarded & ~filters.via_bot)
async def start_command(client, message):
    text = """🐋 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴇᴠᴀʟ ʙᴏᴛ! ✨

📊 ꜰᴏʀ ᴇᴠᴀʟᴜᴀᴛɪᴏɴ ᴀɴᴅ ɪɴꜰᴏ, ꜱɪᴍᴘʟʏ ᴛʏᴘᴇ ʙᴏᴛ ᴀᴄᴛɪᴠɪᴛʏ ʙᴇʟᴏᴡ!

🌟 ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛᴏ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ ʀᴇᴀᴄᴛ ᴡɪᴛʜ ᴡɪᴛᴛʏ ꜰᴇᴇᴅʙᴀᴄᴋ!"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Owner", url="https://t.me/your_owner_link")],
        [InlineKeyboardButton("🔔 Updates", url="https://t.me/your_update_link")],
        [InlineKeyboardButton("🛠 Support", url="https://t.me/your_support_link")]
    ])

    await message.reply_text(text, reply_markup=keyboard)

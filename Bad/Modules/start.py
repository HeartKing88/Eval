from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Bad import app

@app.on_message(filters.command("start") & ~filters.forwarded & ~filters.via_bot)
async def start_command(client, message):
    # Start command message delete karne ke liye
    await message.delete()

    text = """🐋 **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴇᴠᴀʟ ʙᴏᴛ**! ✨

📊 **ꜰᴏʀ ᴇᴠᴀʟᴜᴀᴛɪᴏɴ ᴀɴᴅ ɪɴꜰᴏ, ꜱɪᴍᴘʟʏ ᴛʏᴘᴇ ʙᴏᴛ ᴀᴄᴛɪᴠɪᴛʏ ʙᴇʟᴏᴡ**!

🌟 **ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛᴏ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ ʀᴇᴀᴄᴛ ᴡɪᴛʜ ᴡɪᴛᴛʏ ꜰᴇᴇᴅʙᴀᴄᴋ**!

💫 **ꜰᴏʀ ᴅᴇᴛᴀɪʟᴇᴅ ᴜꜱᴀɢᴇ , ᴛʏᴘᴇ /help ꜰᴏʀ ᴍᴏʀᴇ ɪɴꜰᴏ**! 📖"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 ᴏᴡɴᴇʀ", url="https://t.me/Its_ydv_vikky")],
        [InlineKeyboardButton("🔔 sᴜᴘᴘᴏʀᴛ", url="https://t.me/Exampurrs"), InlineKeyboardButton("🛠 ᴜᴘᴅᴀᴛᴇ", url="https://t.me/FONT_CHANNEL_01")]
    ])

    # URL of the image you want to include
    image_url = "https://ibb.co/V0dLfF32"

    # Send the photo with the text and keyboard
    await message.reply_photo(photo=image_url, caption=text, reply_markup=keyboard)

from pyrogram import Client, filters
from pyrogram.types import Message
from Bad import app  # Aapke bot ka module

# 📌 /id Command
@app.on_message(filters.command("id") & (filters.private | filters.group))
def get_id(client: Client, message: Message):
    chat_id = message.chat.id
    message_id = message.message_id

    # Try to delete the command message
    client.delete_messages(chat_id, message_id)

    args = message.command[1:]  # /id ke baad arguments

    if message.reply_to_message:  # Agar reply kiya hai
        user = message.reply_to_message.from_user
        message.reply_text(f"👤 **User ID:** `{user.id}`")

    elif args:  # Agar /id ke baad koi username ya ID diya gaya hai
        user_or_chat = args[0]
        try:
            entity = client.get_chat(user_or_chat)  # Username ya ID se chat fetch karega
            message.reply_text(f"📌 **{entity.title or entity.first_name}**\n🆔 **ID:** `{entity.id}`")
        except:
            message.reply_text("❌ Invalid username or ID.")

    else:  # Agar sirf /id likha hai bina kisi reply ya argument ke
        if message.chat.type == "private":
            message.reply_text(f"👤 **Your ID:** `{message.chat.id}`")  # PM me user ka ID
        else:
            message.reply_text(f"👥 **Group/Channel/User ID:** `{message.chat.id}`")  # Group ya channel me ID


# 📌 /info Command
@app.on_message(filters.command("info") & (filters.private | filters.group))
def get_info(client: Client, message: Message):
    chat_id = message.chat.id
    message_id = message.message_id

    # Try to delete the command message
    client.delete_messages(chat_id, message_id)

    args = message.command[1:]  # /info ke baad arguments

    if message.reply_to_message:  # Agar reply kiya hai
        user = message.reply_to_message.from_user

    elif args:  # Agar /info ke baad user ID ya username diya gaya hai
        user_or_chat = args[0]
        try:
            user = client.get_users(user_or_chat)
        except:
            message.reply_text("❌ Invalid username or user ID.")
            return
    else:  # Agar sirf /info likha hai bina kisi reply ya argument ke
        user = message.from_user

    # User ka bio fetch karna
    try:
        user_info = client.get_chat(user.id)
        bio = user_info.bio or "N/A"
    except:
        bio = "N/A"

    # Username aur name change history (optional, agar available ho)
    last_username_change = "Unknown"
    last_name_change = "Unknown"
    
    if hasattr(user, "username") and user.username:
        last_username_change = f"@{user.username}"
    
    if hasattr(user, "first_name") and user.first_name:
        last_name_change = f"{user.first_name} {user.last_name or ''}"

    # User Info Format
    info_text = (
        f"👤 **User Info:**\n"
        f"🔹 **Name:** {user.first_name} {user.last_name or ''}\n"
        f"🔹 **Username:** @{user.username if user.username else 'N/A'}\n"
        f"🔹 **ID:** `{user.id}`\n"
        f"🔹 **Bio:** {bio}\n"
    )
    
    message.reply_text(info_text)

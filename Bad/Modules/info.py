from pyrogram import Client, filters
from pyrogram.types import Message
from Bad import app  # Aapke bot ka module

# 📌 /id Command
@app.on_message(filters.command("id") & (filters.private | filters.group))
def get_id(client: Client, message: Message):
    chat_id = message.chat.id
    message_id = message.id  # FIX: `.message_id` ki jagah `.id` use kiya

    # Try to delete the command message
    try:
        client.delete_messages(chat_id, message_id)
    except:
        pass

    args = message.command[1:]

    if message.reply_to_message:
        user = message.reply_to_message.from_user
        message.reply_text(f"👤 **User ID:** `{user.id}`")

    elif args:
        user_or_chat = args[0]
        try:
            entity = client.get_chat(user_or_chat)
            message.reply_text(f"📌 **{entity.title or entity.first_name}**\n🆔 **ID:** `{entity.id}`")
        except:
            message.reply_text("❌ Invalid username or ID.")

    else:
        if message.chat.type == "private":
            message.reply_text(f"👤 **Your ID:** `{message.chat.id}`")
        else:
            message.reply_text(f"👥 **Group/Channel/User ID:** `{message.chat.id}`")


# 📌 /info Command
@app.on_message(filters.command("info") & (filters.private | filters.group))
def get_info(client: Client, message: Message):
    chat_id = message.chat.id
    message_id = message.id  # FIX: `.message_id` ki jagah `.id` use kiya

    # Try to delete the command message
    try:
        client.delete_messages(chat_id, message_id)
    except:
        pass

    args = message.command[1:]

    if message.reply_to_message:
        user = message.reply_to_message.from_user

    elif args:
        user_or_chat = args[0]
        try:
            user = client.get_users(user_or_chat)
        except:
            message.reply_text("❌ Invalid username or user ID.")
            return
    else:
        user = message.from_user

    # User ka bio fetch karna
    try:
        user_info = client.get_chat(user.id)
        bio = user_info.bio or "N/A"
    except:
        bio = "N/A"

    last_username_change = f"@{user.username}" if user.username else "Unknown"
    last_name_change = f"{user.first_name} {user.last_name or ''}"

    info_text = (
        f"👤 **User Info:**\n"
        f"🔹 **Name:** {user.first_name} {user.last_name or ''}\n"
        f"🔹 **Username:** @{user.username if user.username else 'N/A'}\n"
        f"🔹 **ID:** `{user.id}`\n"
        f"🔹 **Bio:** {bio}\n"
        f"🔹 **Last Username Change:** {last_username_change}\n"
        f"🔹 **Last Name Change:** {last_name_change}\n"
        f"🔹 **Is Bot:** {'✅' if user.is_bot else '❌'}\n"
        f"🔹 **Is Premium:** {'✅' if user.is_premium else '❌'}"
    )

    message.reply_text(info_text)

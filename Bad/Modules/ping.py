import time
from Bad import application
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext

async def ping(update: Update, context: CallbackContext) -> None:
    start_time = time.time()
    message = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    
    ping_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
    
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=f"⏳ {ping_time} ms", callback_data="ping_response")]]
    )

    await message.edit_text(f"🏓 Pong! {ping_time} ms", reply_markup=keyboard)

async def ping_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer("This is the bot's response time!")
    
app_instance = application
app_instance.add_handler(CommandHandler("ping", ping))

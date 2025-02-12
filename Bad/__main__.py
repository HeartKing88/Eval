import logging
import asyncio
import importlib
from Bad import app, Bad, Shizu, Sukh  # Import all clients
from pyrogram import idle
from telethon.sessions import StringSession
import Config
from telethon import TelegramClient

# Logger Handler
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

# Main Function
async def main():
    await app.start()
    await Bad.start()

    # Start Pyrogram User Session if available
    if Config.STRING1:
        try:
            await Shizu.start()
            LOGGER("Shizu").info("Shizu (Pyrogram User Session) started successfully.")
        except Exception as e:
            LOGGER("Shizu").error(f"Failed to start Shizu: {e}")

    # Start Telethon User Session if available
    if Config.STRING2:
        try:
            await Sukh.start()
            LOGGER("Sukh").info("Sukh (Telethon User Session) started successfully.")
        except Exception as e:
            LOGGER("Sukh").error(f"Failed to start Sukh: {e}")

    for all_module in ALL_MODULES:
        importlib.import_module("Bad.Modules." + all_module)

    LOGGER("Bad.Modules").info("Successfully Imported Modules...")
    LOGGER("Bad").info("Bot Started Successfully...")

    # Send message to Logger group
    try:
        await app.send_message(Config.LOGGER_ID, "✅ **Bot Started Successfully!**")
        LOGGER("Bad").info("Start message sent to LOGGER_ID.")
    except Exception as e:
        LOGGER("Bad").error(f"Failed to send start message: {e}")

    await idle()

    # Stop all clients properly
    await app.stop()
    await Bad.disconnect()

    if Config.STRING1:
        await Shizu.stop()

    if Config.STRING2:
        await Sukh.disconnect()

    LOGGER("Bad").info("Stopping Bot...")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

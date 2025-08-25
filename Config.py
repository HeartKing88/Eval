from os import getenv
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Get this value from my.telegram.org/apps
APP_ID = 25742938
# Get this value from my.telegram.org/apps
HASH_ID = "b35b715fe8dc0a58e8048988286fc5b6"
# Get your token from @BotFather on Telegram.
TOKEN = "7555900475:AAF5PG9ScYXLjfa1mHUvbyImnX_6nSI3xUc"
DB_NAME = "evalDB"
#databse
MONGO_URL = "mongodb+srv://vikky:vikky@vikky.lkjei.mongodb.net/?retryWrites=true&w=majority&appName=Vikky"
LOGGER_ID = "-1003043427267"
OWNER_ID = "7548614955"
SUDOERS = "7548614955"
STRING1 = ""
STRING2 = ""

#DATABSE
mongo = MongoClient(MONGO_URL)

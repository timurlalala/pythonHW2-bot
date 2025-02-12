import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPEN_WEATHER_MAP_TOKEN= os.getenv("OPEN_WEATHER_MAP_TOKEN")
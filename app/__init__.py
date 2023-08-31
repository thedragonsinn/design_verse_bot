import os

from dotenv import load_dotenv

load_dotenv("config.env")

from app.config import Config
from app.core.db import DB
from app.core.client.client import BOT

if not os.environ.get("TERMUX_APK_RELEASE"):
    import uvloop
    uvloop.install()

bot = BOT()

import json
import os


class Config:

    ADMIN_CHAT = int(os.environ.get("ADMIN_CHAT"))

    CMD_DICT = {}

    CALLBACK_DICT = {}

    CONV_DICT = {}

    DEV_MODE = int(os.environ.get("DEV_MODE", 0))

    DB_URL = os.environ.get("DB_URL")

    MAIN_CHAT = int(os.environ.get("MAIN_CHAT"))

    LOG_CHAT = int(os.environ.get("LOG_CHAT"))

    TRIGGER = "/"

    USERS = json.loads(os.environ.get("USERS", "[]"))

    USER_CMD_DICT = {}

    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", "https://github.com/thedragonsinn/design_verse_bot")
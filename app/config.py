import json
import os
from typing import Coroutine


class Config:
    ADMIN_CHAT: int = int(os.environ.get("ADMIN_CHAT"))

    CMD_DICT: dict[Coroutine] = {}

    CALLBACK_DICT: dict[Coroutine] = {}

    CONV_DICT: dict[Coroutine] = {}

    DEV_MODE: int = int(os.environ.get("DEV_MODE", 0))

    DB_URL: str = os.environ.get("DB_URL")

    MAIN_CHAT: int = int(os.environ.get("MAIN_CHAT"))

    LOG_CHAT: int = int(os.environ.get("LOG_CHAT"))

    TRIGGER: str = "/"

    USERS: list[int] = json.loads(os.environ.get("USERS", "[]"))

    USER_CMD_DICT: dict[Coroutine] = {}

    UPSTREAM_REPO: str = os.environ.get(
        "UPSTREAM_REPO", "https://github.com/thedragonsinn/design_verse_bot"
    )

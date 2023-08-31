import glob
import importlib
import os
import sys
from functools import wraps
from io import BytesIO

from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from app import DB, Config
from app.core import Message
from app.utils import aiohttp_tools


class BOT(Client):
    def __init__(self):
        super().__init__(
            name="bot",
            api_id=int(os.environ.get("API_ID")),
            api_hash=os.environ.get("API_HASH"),
            bot_token=os.environ.get("BOT_TOKEN"),
            in_memory=False,
            parse_mode=ParseMode.DEFAULT,
            sleep_threshold=30,
            max_concurrent_transmissions=2,
        )

    def add_cmd(self, cmd, cb: bool = False, user: bool = False):
        def the_decorator(func):
            @wraps(func)
            def wrapper():
                config_dict = Config.CMD_DICT
                if cb:
                    config_dict = Config.CALLBACK_DICT
                if user:
                    config_dict = Config.USER_CMD_DICT
                if isinstance(cmd, list):
                    for _cmd in cmd:
                        config_dict[_cmd] = func
                else:
                    config_dict[cmd] = func

            wrapper()
            return func

        return the_decorator

    async def boot(self):
        await super().start()
        await self.import_modules()
        await aiohttp_tools.session_switch()
        await self.edit_restart_msg()
        await self.log(text="<i>Started</i>")
        print("started")
        await idle()
        await aiohttp_tools.session_switch()
        DB._client.close()

    async def edit_restart_msg(self):
        restart_msg = int(os.environ.get("RESTART_MSG", 0))
        restart_chat = int(os.environ.get("RESTART_CHAT", 0))
        if restart_msg and restart_chat:
            await super().get_chat(restart_chat)
            await super().edit_message_text(
                chat_id=restart_chat, message_id=restart_msg, text="__Started__"
            )
            os.environ.pop("RESTART_MSG", "")
            os.environ.pop("RESTART_CHAT", "")

    async def import_modules(self):
        for py_module in glob.glob("app/**/*.py", recursive=True):
            name = os.path.splitext(py_module)[0]
            py_name = name.replace("/", ".")
            importlib.import_module(py_name)

    async def log(
        self,
        text="",
        traceback="",
        chat=None,
        func=None,
        name="log.txt",
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML,
    ):
        if traceback:
            text = f"#Traceback\n<b>Function:</b> {func}\n<b>Chat:</b> {chat}\n<b>Traceback:</b>\n<code>{traceback}</code>"
        return await self.send_message(
            chat_id=Config.LOG_CHAT,
            text=text,
            name=name,
            disable_web_page_preview=disable_web_page_preview,
            parse_mode=parse_mode,
        )

    async def restart(self, hard=False):
        await aiohttp_tools.session_switch()
        await super().stop(block=False)
        DB._client.close()
        args = [sys.executable, sys.executable, "-m", "app"]
        if hard:
            os.execle(*args, {})
        os.execl(*args)

    async def send_message(self, chat_id, text, name: str = "output.txt", **kwargs):
        if len(str(text)) < 4096:
            return Message.parse_message(
                (await super().send_message(chat_id=chat_id, text=text, **kwargs))
            )
        doc = BytesIO(bytes(text, encoding="utf-8"))
        doc.name = name
        kwargs.pop("disable_web_page_preview", "")
        return await super().send_document(chat_id=chat_id, document=doc, **kwargs)

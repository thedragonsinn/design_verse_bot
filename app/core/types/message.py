import asyncio
from functools import cached_property

from pyrogram.errors import MessageDeleteForbidden
from pyrogram.types import Message as Msg

from app import Config


class Message(Msg):
    def __init__(self, message: Msg) -> None:
        super().__dict__.update(message.__dict__)

    @cached_property
    def cmd(self) -> str | None:
        raw_cmd = self.text_list[0]
        cmd = raw_cmd.lstrip(Config.TRIGGER)
        return cmd if cmd in Config.CMD_DICT or cmd in Config.CMD_DICT or cmd in Config.USER_CMD_DICT else None

    @cached_property
    def flags(self) -> list:
        return [i for i in self.text_list if i.startswith("-")]

    @cached_property
    def flt_input(self) -> str:
        split_lines = self.input.splitlines()
        split_n_joined = [
            " ".join([word for word in line.split(" ") if word not in self.flags])
            for line in split_lines
        ]
        return "\n".join(split_n_joined)

    @cached_property
    def input(self) -> str:
        if len(self.text_list) > 1:
            return self.text.split(maxsplit=1)[-1]
        return ""

    @cached_property
    def replied(self) -> "Message":
        if self.reply_to_message:
            return Message.parse_message(self.reply_to_message)

    @cached_property
    def reply_id(self) -> int | None:
        return self.replied.id if self.replied else None

    @cached_property
    def replied_task_id(self) -> str | None:
        return self.replied.task_id if self.replied else None

    @cached_property
    def task_id(self) -> str:
        return f"{self.chat.id}-{self.id}"

    @cached_property
    def text_list(self) -> list:
        return self.text.split()

    async def async_deleter(self, del_in, task, block) -> None:
        if block:
            x = await task
            await asyncio.sleep(del_in)
            await x.delete()
        else:
            asyncio.create_task(
                self.async_deleter(del_in=del_in, task=task, block=True)
            )

    async def delete(self, reply: bool = False) -> None:
        try:
            await super().delete()
            if reply and self.replied:
                await self.replied.delete()
        except MessageDeleteForbidden:
            pass

    async def edit(self, text, del_in: int = 0, block=True, **kwargs) -> "Message":
        if len(str(text)) < 4096:
            kwargs.pop("name", "")
            task = self.edit_text(text, **kwargs)
            if del_in:
                reply = await self.async_deleter(task=task, del_in=del_in, block=block)
            else:
                reply = await task
        else:
            _, reply = await asyncio.gather(
                super().delete(), self.reply(text, **kwargs)
            )
        return reply

    async def reply(
        self, text, del_in: int = 0, block: bool = True, **kwargs
    ) -> "Message":
        task = self._client.send_message(
            chat_id=self.chat.id, text=text, reply_to_message_id=self.id, **kwargs
        )
        if del_in:
            await self.async_deleter(task=task, del_in=del_in, block=block)
        else:
            return await task

    @classmethod
    def parse_message(cls, message: Msg) -> "Message":
        return cls(message)

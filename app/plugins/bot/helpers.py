import asyncio
from async_lru import alru_cache
from typing import Iterable

from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton
from pyrogram.types.user_and_chats import ChatMember

from app import Config, bot
from app.core import Message


async def sleeper(u_id: int) -> None:
    c_dict: dict = Config.CONV_DICT
    c_dict[u_id] = False
    try:
        async with asyncio.timeout(300):
            while not c_dict[u_id]:
                await asyncio.sleep(1)
    except TimeoutError:
        c_dict[u_id] = "Timeout."


async def get_messages(chat_id: str | int, msg_ids: list | int) -> list[Message] | None:
    msgs = await bot.get_messages(chat_id=chat_id, message_ids=msg_ids)
    ret_msgs = [msg for msg in msgs if msg.from_user.id != bot.me.id]
    return ret_msgs if len(ret_msgs) <= 5 else None


async def forward_messages(messages: list) -> None:
    for message in messages:
        await message.forward(Config.ADMIN_CHAT)
        await asyncio.sleep(1)


def make_buttons(button_data: Iterable) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text=data[0], callback_data=str(data[1]))
        for data in button_data
    ]


@alru_cache()
async def check_member(u_id: int) -> ChatMember | None:
    try:
        return await bot.get_chat_member(Config.MAIN_CHAT, u_id)
    except UserNotParticipant:
        return


@alru_cache()
async def get_welcome_banner() -> Message:
    return await bot.get_messages(chat_id=Config.LOG_CHAT, message_ids=33)

import asyncio

from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton

from app import Config, bot


async def sleeper(u_id):
    c_dict = Config.CONV_DICT
    c_dict[u_id] = False
    try:
        async with asyncio.timeout(300):
            while not c_dict[u_id]:
                await asyncio.sleep(1)
    except TimeoutError:
        c_dict[u_id] = "Timeout."


async def get_messages(chat_id, msg_ids):
    msgs = await bot.get_messages(chat_id=chat_id, message_ids=msg_ids)
    ret_msgs = [msg for msg in msgs if msg.from_user.id != bot.me.id]
    return ret_msgs if len(ret_msgs) <= 5 else None


async def forward_messages(messages: list):
    for message in messages:
        await message.forward(Config.ADMIN_CHAT)
        await asyncio.sleep(1)


def make_buttons(button_data):
    return [
        InlineKeyboardButton(text=data[0], callback_data=str(data[1]))
        for data in button_data
    ]


async def check_member(u_id):
    try:
        return await bot.get_chat_member(Config.MAIN_CHAT, u_id)
    except UserNotParticipant:
        return

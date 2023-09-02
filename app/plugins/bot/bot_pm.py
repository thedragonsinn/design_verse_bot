import asyncio

from pyrogram.types import InlineKeyboardMarkup

from app import DB, Config, bot
from app.core import Message
from app.plugins.bot.helpers import check_member, make_buttons
from app.utils.db_utils import add_data, extract_user_data


@bot.add_cmd(cmd="done", user=True)
async def done(bot: bot, message: Message):
    u_id = message.from_user.id
    if u_id not in Config.CONV_DICT:
        return await message.reply("That command was out of place.")
    Config.CONV_DICT[u_id] = message.id


@bot.add_cmd(cmd="cancel", user=True)
async def done(bot: bot, message: Message):
    u_id = message.from_user.id
    if u_id not in Config.CONV_DICT:
        return await message.reply("That command was out of place.")
    Config.CONV_DICT[u_id] = "Cancelled."


@bot.add_cmd(cmd="start", user=True)
async def start(bot: bot, message: Message):
    coros = (message.reply("Welcome."),
        add_data(
        DB.USERS,
        id=message.from_user.id,
        data={"user": extract_user_data(message.from_user)},
        ),
        bot.log(text=f"{message.from_user.mention} started the bot."))
    await asyncio.gather(*coros)

@bot.add_cmd(cmd="submit", user=True)
async def submit(bot: bot, message: Message):
    button_list = [("Banner Request", dict(cmd="banner_confirmation"))]
    if not await check_member(message.from_user.id):
        button_list.append(("Join Request", dict(cmd="join_confirmation")))
    buttons = make_buttons(button_list)
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"What do you want to do?",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )

import asyncio
from datetime import datetime

from pyrogram.types import InlineKeyboardMarkup

from app import DB, Config, bot
from app.core import CallbackQuery
from app.plugins.bot.helpers import (
    forward_messages,
    get_messages,
    make_buttons,
    sleeper,
)
from app.utils.db_utils import add_data

# Banner Request Template
BRT = """
You can request for a banner by filling out the form below:

1) The name of the project you want the banner for along with their logo ( if available ).
2) What info should the banner contain? , along with any sample layout you might want the banner to be in .
3) Within how many days do you want the banner ?

Do note that if your request is accepted you will be contacted by the admin that accepted you ( Logo requests will be rejected , if you don't bribe us that is )

Send /done when you are done submitting your work or /cancel to cancel.
"""

DB_NAME = DB.BANNER_REQUESTS


@bot.add_cmd(cmd="banner_confirmation", cb=True)
async def handle_confirmation(bot: bot, cb: CallbackQuery):
    cooldown = await check_cooldown(cb.from_user.id)
    if cooldown:
        return await cb.edit_message_text(cooldown)
    buttons = make_buttons(
        [("yes", dict(cmd="banner_request_yes")), ("no", dict(cmd="cancel_request"))]
    )
    await cb.edit_message_text(
        text=f"You can Request only once a week.\nProceed?",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


@bot.add_cmd(cmd="banner_request_yes", cb=True)
async def banner_request_submitter(bot: bot, cb: CallbackQuery):
    u_id = cb.from_user.id
    await cb.edit_message_text(BRT)
    await sleeper(u_id)
    if Config.CONV_DICT[u_id] in {"Cancelled.", "Timeout."}:
        await bot.send_message(
            chat_id=u_id,
            text=f"{Config.CONV_DICT[u_id]}\nSend /submit again to start over.",
        )
        return Config.CONV_DICT.pop(u_id, "")
    msg_id = Config.CONV_DICT.pop(u_id)
    messages = await get_messages(
        chat_id=u_id, msg_ids=[i for i in range(cb.message.id, msg_id)]
    )
    if not messages:
        return await bot.send_message(
            chat_id=u_id, text="Send 1-5 messages max.\nSend /submit to start over."
        )
    await asyncio.gather(
        add_data(DB_NAME, id=u_id, data={"banner_request_datetime": datetime.now()}),
        bot.send_message(chat_id=u_id, text="Request Received."),
    )
    await forward_messages(messages)
    buttons = make_buttons(
        [
            ("accept", dict(cmd="accept_banner_request", user=u_id)),
            ("ban", dict(cmd="ban", user=u_id)),
        ]
    )
    await bot.send_message(
        chat_id=Config.ADMIN_CHAT,
        text=f"{cb.from_user.mention} sent a banner request.",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


async def check_cooldown(u_id):
    user = await DB_NAME.find_one({"_id": u_id})
    if not user:
        await add_data(DB_NAME, id=u_id, data={"count": 1})
        return
    date = user.get("banner_request_datetime")
    accepted = user.get("accepted")
    if date:
        cooldown = (datetime.now() - date).days
        # If It's been more than 7 days allow user to make new request
        if cooldown > 7:
            return
        # if a request is accepted but it's not been a week, they've already
        # used up their one request per week.
        if accepted and cooldown < 7:
            return "Our requests are currently full, please wait for the next week and retry ! "
        # If it's not accepted but it's not been a week ask to wait another 7
        # days to try again.
        if not accepted and cooldown < 7:
            return "Hey there !\nWe are currently taking only 1 request per week and keep in mind that if no admin takes the job within a day it will get cancelled automatically!"
    await add_data(DB_NAME, id=u_id, data={"count": user.get("count", 0) + 1})


@bot.add_cmd(cmd="accept_banner_request", cb=True)
async def handle_request(bot: bot, cb: CallbackQuery):
    user = await bot.get_users(cb.cbdata["user"])
    await bot.send_message(
        chat_id=user.username or user.id,
        text=f"{cb.from_user.mention} has accepted your Banner request.\nThey will contact you soon.",
    )
    await cb.edit_message_text(
        f"User:{user.mention} 's Banner request has been accepted by {cb.from_user.mention} "
    )
    await add_data(DB_NAME, id=user.id, data=dict(accepted=True))

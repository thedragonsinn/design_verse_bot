import asyncio
from datetime import datetime, timedelta

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

# Join Request Template
JRT = """Hey there!
To join Design Verse, please submit your portfolio (any work you have done) in the following format:

1. Your name
2. Why do you want to join Design Verse?
3. A link to your portfolio (or send your work to the bot in the form of a file. Maximum files allowed: 5 )

Send /done when you are done submitting your work or /cancel to cancel."""

DB_NAME = DB.USERS


@bot.add_cmd(cmd="join_confirmation", cb=True)
async def handle_confirmation(bot, qb):
    date = (await DB_NAME.find_one({"_id": qb.from_user.id})).get(
        "join_request_datetime"
    )
    if date:
        cooldown = (datetime.now() - date).days
        if cooldown < 7:
            return await qb.edit_message_text(
                f"Hey there !\nOur requests are currently full, please wait for the next week and retry ! "
            )
    buttons = make_buttons(
        [("yes", dict(cmd="join_request_yes")), ("no", dict(cmd="cancel_request"))]
    )
    await qb.edit_message_text(
        text=f"You can Request only once a week.\nProceed?",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


@bot.add_cmd(cmd="join_request_yes", cb=True)
async def join_request_submitter(bot: bot, qb: CallbackQuery):
    await qb.edit_message_text(JRT)
    u_id = qb.from_user.id
    await sleeper(u_id)
    if Config.CONV_DICT[u_id] in {"Cancelled.", "Timeout."}:
        await bot.send_message(
            chat_id=u_id,
            text=f"{Config.CONV_DICT[u_id]}\nSend /submit again to start over.",
        )
        return Config.CONV_DICT.pop(u_id, "")
    msg_id = Config.CONV_DICT.pop(u_id)
    messages = await get_messages(
        chat_id=u_id, msg_ids=[i for i in range(qb.message.id, msg_id)]
    )
    if not messages:
        return await bot.send_message(
            chat_id=u_id, text="Send 1-5 messages max.\nSend /submit to start over."
        )
    await asyncio.gather(
        add_data(DB_NAME, id=u_id, data={"join_request_datetime": datetime.now()}),
        bot.send_message(chat_id=u_id, text="Request Received."),
    )
    await forward_messages(messages)
    buttons = make_buttons(
        [
            ("accept", dict(cmd="accept_join_request", user=u_id)),
            ("reject", dict(cmd="reject_join_request", user=u_id)),
            ("ban", dict(cmd="ban", user=u_id)),
        ]
    )
    await bot.send_message(
        chat_id=Config.ADMIN_CHAT,
        text=f"{qb.from_user.mention} sent a join request.",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


@bot.add_cmd(cmd=["accept_join_request", "reject_join_request"], cb=True)
async def handle_request(bot: bot, qb: CallbackQuery):
    user = await bot.get_users(qb.qbdata["user"])
    if qb.qbdata["cmd"] == "reject_join_request":
        await bot.send_message(
            chat_id=user.id,
            text=f"Your Join request has been rejected\nYou can try again in 7days.",
        )
        await qb.edit_message_text(
            f"User:{user.mention}'s Join request has been rejected by {qb.from_user.mention}"
        )
        return
    expiry = datetime.now() + timedelta(days=3)
    link = await bot.create_chat_invite_link(
        chat_id=Config.MAIN_CHAT, member_limit=1, expire_date=expiry
    )
    await bot.send_message(chat_id=user.username or user.id, text=link.invite_link)
    await qb.edit_message_text(
        f"User:{user.mention}\nHas been accepted by {qb.from_user.mention}\nChat Invite link Sent."
    )

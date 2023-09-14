import asyncio
from datetime import datetime, timedelta

from motor.core import AgnosticCollection
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types.user_and_chats import User

from app import DB, Config, bot
from app.core import CallbackQuery, Message
from app.plugins.bot.helpers import (
    forward_messages,
    get_messages,
    make_buttons,
    sleeper,
)
from app.utils.db_utils import add_data

# Join Request Template
JRT = """
Hello,

To apply for membership in Design Verse, kindly provide your portfolio in the following format:

1. Your full name.
2. The reason for your interest in joining Design Verse.
3. Please share a link to your portfolio, or alternatively, send your work to the bot as files (you can send up to 5 files).

When you have completed your submission, send /done to confirm, or use /cancel to cancel your application.
"""

DB_NAME: AgnosticCollection = DB.USERS


@bot.add_cmd(cmd="join_confirmation", cb=True)
async def handle_confirmation(bot: bot, cb: CallbackQuery) -> None | Message:
    date: datetime = (await DB_NAME.find_one({"_id": cb.from_user.id})).get(
        "join_request_datetime"
    )
    if date:
        cooldown = (datetime.now() - date).days
        if cooldown < 7:
            return await cb.edit_message_text(
                f"Hey there !\nOur requests are currently full, please wait for the next week and retry ! "
            )
    buttons: list[InlineKeyboardButton] = make_buttons(
        [("yes", dict(cmd="join_request_yes")), ("no", dict(cmd="cancel_request"))]
    )
    await cb.edit_message_text(
        text=f"You can Request only once a week.\nProceed?",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


@bot.add_cmd(cmd="join_request_yes", cb=True)
async def join_request_submitter(bot: bot, cb: CallbackQuery) -> None | Message:
    await cb.edit_message_text(JRT)
    u_id: int = cb.from_user.id
    await sleeper(u_id)
    if Config.CONV_DICT[u_id] in {"Cancelled.", "Timeout."}:
        await bot.send_message(
            chat_id=u_id,
            text=f"{Config.CONV_DICT[u_id]}\nSend /submit again to start over.",
        )
        return Config.CONV_DICT.pop(u_id, "")
    msg_id: int = Config.CONV_DICT.pop(u_id)
    messages: list[Message] = await get_messages(
        chat_id=u_id, msg_ids=[i for i in range(cb.message.id, msg_id)]
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
    buttons: list[InlineKeyboardButton] = make_buttons(
        [
            ("accept", dict(cmd="accept_join_request", user=u_id)),
            ("reject", dict(cmd="reject_join_request", user=u_id)),
            ("ban", dict(cmd="ban", user=u_id)),
        ]
    )
    await bot.send_message(
        chat_id=Config.ADMIN_CHAT,
        text=f"{cb.from_user.mention} sent a join request.",
        reply_markup=InlineKeyboardMarkup([buttons]),
    )


@bot.add_cmd(cmd=["accept_join_request", "reject_join_request"], cb=True)
async def handle_request(bot: bot, cb: CallbackQuery) -> None:
    user: User = await bot.get_users(cb.cb_data["user"])
    if cb.cb_data["cmd"] == "reject_join_request":
        await bot.send_message(
            chat_id=user.id,
            text=f"Your Join request has been rejected\nYou can try again in 7days.",
        )
        await cb.edit_message_text(
            f"User:{user.mention}'s Join request has been rejected by {cb.from_user.mention}"
        )
        return
    expiry = datetime.now() + timedelta(days=3)
    link = await bot.create_chat_invite_link(
        chat_id=Config.MAIN_CHAT, member_limit=1, expire_date=expiry
    )
    await bot.send_message(chat_id=user.username or user.id, text=link.invite_link)
    await cb.edit_message_text(
        f"User:{user.mention}\nHas been accepted by {cb.from_user.mention}\nChat Invite link Sent."
    )

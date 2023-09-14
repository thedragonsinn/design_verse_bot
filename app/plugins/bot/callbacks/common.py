from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types.user_and_chats import User

from app import DB, bot
from app.core import CallbackQuery, Message
from app.plugins.bot.helpers import make_buttons
from app.utils.db_utils import add_data


@bot.add_cmd(cmd=["ban", "unban"], cb=True)
async def restrict_user(bot: bot, cb: CallbackQuery) -> None:
    user: User = await bot.get_users(cb.cb_data["user"])
    action_by: str = cb.from_user.mention
    if cb.cb_data["cmd"] == "ban":
        await add_data(DB.BANNED, id=user.id, data={"by": cb.from_user.mention})
        await cb.edit_message_text(
            text=f"{action_by} banned {user.mention}",
            reply_markup=InlineKeyboardMarkup(
                [make_buttons([("unban", dict(cmd="unban", user=user.id))])]
            ),
        )
        await bot.send_message(
            chat_id=user.id, text="You've been banned from using the bot."
        )
    else:
        await DB.BANNED.delete_one({"_id": user.id})
        await cb.edit_message_text(f"{action_by} unbanned {user.mention}")
        await bot.send_message(chat_id=user.id, text="You've been unbanned.")


@bot.add_cmd(cmd="cancel_request", cb=True)
async def join_request_submitter(bot: bot, cb: CallbackQuery) -> Message:
    return await cb.edit_message_text(f"Submission Cancelled.")

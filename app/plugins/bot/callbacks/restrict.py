from pyrogram.types import InlineKeyboardMarkup

from app import DB, bot
from app.core import CallbackQuery
from app.plugins.bot.helpers import make_buttons
from app.utils.db_utils import add_data


@bot.add_cmd(cmd=["ban", "unban"], cb=True)
async def restrict_user(bot: bot, qb: CallbackQuery):
    user = await bot.get_users(qb.qbdata["user"])
    action_by = qb.from_user.mention
    if qb.qbdata["cmd"] == "ban":
        await add_data(DB.BANNED, id=user.id, data={"by": qb.from_user.mention})
        await qb.edit_message_text(
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
        await qb.edit_message_text(f"{action_by} unbanned {user.mention}")
        await bot.send_message(chat_id=user.id, text="You've been unbanned.")

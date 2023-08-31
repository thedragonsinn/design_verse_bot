import asyncio
import traceback
from datetime import datetime

from pyrogram.enums import ChatType

from app import DB, Config, bot
from app.core import CallbackQuery, Message, filters


@bot.on_message(filters.cmd_filter)
@bot.on_edited_message(filters.cmd_filter)
async def cmd_dispatcher(bot, message):
    message = Message.parse_message(message)
    func = Config.CMD_DICT[message.cmd]
    coro = func(bot, message)
    await run_coro(coro, message)


@bot.on_message(filters.user_filter)
async def cmd_dispatcher(bot: bot, message):
    banned = await DB.BANNED.find_one({"_id": message.from_user.id})
    if banned:
        return
    message = Message.parse_message(message)
    func = Config.USER_CMD_DICT[message.cmd]
    coro = func(bot, message)
    await run_coro(coro, message)


@bot.on_callback_query()
async def callback_handler(bot: bot, qb):
    if (
        qb.message.chat.type == ChatType.PRIVATE
        and (datetime.now() - qb.message.date).total_seconds() > 30
    ):
        return await qb.edit_message_text(f"Query Expired. Try again.")
    banned = await DB.BANNED.find_one({"_id": qb.from_user.id})
    if banned:
        return
    qb = CallbackQuery.parse_qb(qb)
    func = Config.CALLBACK_DICT.get(qb.cmd)
    if not func:
        return
    coro = func(bot, qb)
    await run_coro(coro, message)


async def run_coro(coro, message):
    try:
        task = asyncio.Task(coro, name=message.task_id)
        await task
    except asyncio.exceptions.CancelledError:
        await bot.log(text=f"<b>#Cancelled</b>:\n<code>{message.text}</code>")
    except BaseException:
        await bot.log(
            traceback=str(traceback.format_exc()),
            chat=message.chat.title or message.chat.first_name,
            func=coro.__name__,
            name="traceback.txt",
        )
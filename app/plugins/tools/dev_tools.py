import asyncio
import importlib
import sys
import traceback
from io import StringIO

from pyrogram.enums import ParseMode

from app import Config, bot, DB # isort:skip

from app.utils import shell, aiohttp_tools as aio  # isort:skip


# Run shell commands
async def run_cmd(bot, message):
    cmd = message.input.strip()
    reply = await message.reply("executing...")
    try:
        proc_stdout = await asyncio.Task(shell.run_shell_cmd(cmd), name=reply.task_id)
    except asyncio.exceptions.CancelledError:
        return await reply.edit("`Cancelled...`")
    output = f"~$`{cmd}`\n\n`{proc_stdout}`"
    return await reply.edit(output, name="sh.txt", disable_web_page_preview=True)


# Shell with Live Output
async def live_shell(bot, message):
    cmd = message.input.strip()
    reply = await message.reply("`getting live output....`")
    sub_process = await shell.AsyncShell.run_cmd(cmd)
    sleep_for = 1
    output = ""
    try:
        async for stdout in sub_process.get_output():
            if output != stdout:
                if len(stdout) <= 4096:
                    await reply.edit(
                        f"`{stdout}`",
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                output = stdout
            if sleep_for >= 6:
                sleep_for = 1
            await asyncio.Task(asyncio.sleep(sleep_for), name=reply.task_id)
            sleep_for += 1
        return await reply.edit(
            f"~$`{cmd}\n\n``{sub_process.full_std}`",
            name="shell.txt",
            disable_web_page_preview=True,
        )
    except asyncio.exceptions.CancelledError:
        sub_process.cancel()
        return await reply.edit(f"`Cancelled....`")


# Run Python code


async def executor(bot, message):
    code = message.flt_input.strip()
    if not code:
        return await message.reply("exec Jo mama?")
    reply = await message.reply("executing")
    sys.stdout = codeOut = StringIO()
    sys.stderr = codeErr = StringIO()
    # Indent code as per proper python syntax
    formatted_code = "\n    ".join(code.splitlines())
    try:
        # Create and initialise the function
        exec(f"async def _exec(bot, message):\n    {formatted_code}")
        func_out = await asyncio.Task(
            locals()["_exec"](bot, message), name=reply.task_id
        )
    except asyncio.exceptions.CancelledError:
        return await reply.edit("`Cancelled....`")
    except BaseException:
        func_out = str(traceback.format_exc())
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    output = codeErr.getvalue().strip() or codeOut.getvalue().strip()
    if func_out is not None:
        output = "\n\n".join([output, str(func_out)]).strip()
    if "-s" not in message.flags:
        output = f"> `{code}`\n\n>>  `{output}`"
    return await reply.edit(
        output,
        name="exec.txt",
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )


async def loader(bot, message):
    if (
        not message.replied
        or not message.replied.document
        or not message.replied.document.file_name.endswith(".py")
    ):
        return await message.reply("reply to a plugin.")
    reply = await message.reply("Loading....")
    file_name = message.replied.document.file_name.rstrip(".py")
    reload = sys.modules.pop(f"app.temp.{file_name}", None)
    status = "Reloaded" if reload else "Loaded"
    await message.replied.download("app/temp/")
    try:
        importlib.import_module(f"app.temp.{file_name}")
    except BaseException:
        return await reply.edit(str(traceback.format_exc()))
    await reply.edit(f"{status} {file_name}.py.")


@bot.add_cmd(cmd="c")
async def cancel_task(bot, message):
    task_id = message.replied_task_id
    if not task_id:
        return await message.reply(
            "Reply To a Command or Bot's Response Message.", del_in=8
        )
    all_tasks = asyncio.all_tasks()
    tasks = [x for x in all_tasks if x.get_name() == task_id]
    if not tasks:
        return await message.reply("Task not in Currently Running Tasks.", del_in=8)
    response = ""
    for task in tasks:
        status = task.cancel()
        response += f"Task: __{task.get_name()}__\nCancelled: __{status}__\n"
    await message.reply(response, del_in=5)


if Config.DEV_MODE:
    Config.CMD_DICT["sh"] = run_cmd
    Config.CMD_DICT["shell"] = live_shell
    Config.CMD_DICT["exec"] = executor
    Config.CMD_DICT["load"] = loader

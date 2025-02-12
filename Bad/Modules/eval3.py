import os
import sys
import traceback
from io import StringIO
from time import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from Bad import Jass

async def aexec(code, bot, message):
    exec(
        "async def __aexec(bot, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](bot, message)

async def telegram_eval(update: Update, context: CallbackContext):
    message = update.message
    if message.reply_to_message and message.reply_to_message.document:
        document = message.reply_to_message.document
        if document.file_name.endswith(".py"):
            file_path = await context.bot.get_file(document.file_id).download()
            with open(file_path, "r") as file:
                cmd = file.read()
        else:
            await message.reply_text("<b>Only .py files are supported.</b>")
            return
    elif len(context.args) < 1:
        await message.reply_text("<b>Provide code to evaluate.</b>")
        return
    else:
        cmd = " ".join(context.args)

    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, context.bot, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = "\n"
    if exc:
        evaluation += exc
    elif stderr:
        evaluation += stderr
    elif stdout:
        evaluation += stdout
    else:
        evaluation += "Success"
    final_output = f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n<pre language='python'>{evaluation}</pre>"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation))
        t2 = time()
        await message.reply_document(
            document=open(filename, "rb"),
            caption=f"<b>⥤ ᴇᴠᴀʟ :</b>\n<code>{cmd[0:980]}</code>\n\n<b>⥤ ʀᴇsᴜʟᴛ :</b>\nAttached Document",
        )
        os.remove(filename)
    else:
        t2 = time()
        await message.reply_text(final_output)

# Create the application and add the handler
app = Jass().app
app.add_handler(CommandHandler("eval", telegram_eval))

# Start the application
if __name__ == "__main__":
    app.run_polling()

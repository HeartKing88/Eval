import os
import sys
import traceback
from io import StringIO
from time import time
import textwrap
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from Bad import application  

async def aexec(code, bot, message):
    """Safely executes async Python code."""
    local_vars = {"bot": bot, "message": message}
    
    try:
        exec(f"async def __aexec():\n{textwrap.indent(code, '    ')}", local_vars)
        return await local_vars["__aexec"]()
    except SyntaxError as e:
        return f"SyntaxError: {e}"
    except Exception as e:
        return f"Error: {traceback.format_exc()}"

async def telegram_eval(update: Update, context: CallbackContext):
    message = update.message
    
    if message.reply_to_message and message.reply_to_message.document:
        document = message.reply_to_message.document
        if document.file_name.endswith('.py'):
            file_path = await context.bot.get_file(document.file_id).download()
            with open(file_path, 'r') as file:
                cmd = file.read()
        else:
            await message.reply_text('<b>Only .py files are supported.</b>')
            return
    elif not context.args:
        await message.reply_text('<b>Provide code to evaluate.</b>')
        return
    else:
        cmd = " ".join(context.args)

    t1 = time()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    redirected_output, redirected_error = StringIO(), StringIO()
    sys.stdout, sys.stderr = redirected_output, redirected_error

    stdout, stderr, exc = None, None, None
    try:
        output = await aexec(cmd, context.bot, message)
        stdout = str(output) if output else redirected_output.getvalue()
    except Exception:
        exc = traceback.format_exc()
    
    stderr = redirected_error.getvalue()
    sys.stdout, sys.stderr = old_stdout, old_stderr

    evaluation = '\n'
    if exc:
        evaluation += exc
    elif stderr:
        evaluation += stderr
    elif stdout:
        evaluation += stdout
    else:
        evaluation += 'Success'

    final_output = f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n<pre language='python'>{evaluation}</pre>"

    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation))
        await message.reply_document(
            document=open(filename, "rb"),
            caption=f"<b>⥤ ᴇᴠᴀʟ :</b>\n<code>{cmd[0:980]}</code>\n\n<b>⥤ ʀᴇsᴜʟᴛ :</b>\nAttached Document",
        )
        os.remove(filename)
    else:
        await message.reply_text(final_output)

# Use the existing Jass application instance
app_instance = application
app_instance.add_handler(CommandHandler("eval3", telegram_eval))

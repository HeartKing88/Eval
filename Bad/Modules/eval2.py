import re
import os
import sys
import traceback
from io import StringIO
from time import time
from Bad import app, Bad
from telethon import events, Button
from telethon.tl.custom import Button

@Bad.on(events.NewMessage(pattern='/eval2'))
async def eval_handler(event):
    if event.reply_to and hasattr(event.reply_to, 'media') and event.reply_to.media and event.reply_to.media.document and event.reply_to.media.document.mime_type == 'text/x-python':
        file_path = await event.client.download_media(event.reply_to)
        with open(file_path, "r") as file:
            cmd = file.read()
    elif len(event.raw_text.split()) < 2:
        await event.reply("ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴɴᴀ ᴇxᴇᴄᴜᴛᴇ ʙᴀʙʏ [ᴛᴇʟᴇ] ?")
        return
    else:
        cmd = event.raw_text.split(" ", maxsplit=1)[1]

    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        exec(
            "async def __aexec(event): "
            + "".join(f"\n {a}" for a in cmd.split("\n"))
        )
        await locals()["__aexec"](event)
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
    final_output = f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n```python\n{evaluation}\n```"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation))
        t2 = time()
        keyboard = [
            [Button.inline(f"⏳ {round(t2-t1, 3)} Seconds")],
        ]
        await event.respond(file=filename, buttons=keyboard)
        os.remove(filename)
    else:
        t2 = time()
        keyboard = [
            [Button.inline(f"⏳ {round(t2-t1, 3)} Seconds"), Button.inline("🗑", data=f"forceclose|{event.sender_id}")],
        ]
        await event.respond(final_output, buttons=keyboard)

@Bad.on(events.CallbackQuery(data="forceclose"))
async def forceclose_callback(event):
    data_parts = event.data.decode().split("|")
    if len(data_parts) < 2 or event.sender_id != int(data_parts[1]):
        await event.answer("» ɪᴛ'ʟʟ ʙᴇ ʙᴇᴛᴛᴇʀ ɪғ ʏᴏᴜ sᴛᴀʏ ɪɴ ʏᴏᴜʀ ʟɪᴍɪᴛs ʙᴀʙʏ.", alert=True)
        return
    await event.delete()

@Bad.on(events.CallbackQuery(data=re.compile(b"runtime")))
async def runtime_callback(event):
    runtime = event.data.decode().split(None, 1)[1]
    await event.answer(runtime, alert=True)

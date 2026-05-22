import hashlib
import platform
import requests
import sys
from datetime import datetime


LICENSE_URL = "https://raw.githubusercontent.com/romanzovnuk-sys/Hwiid/refs/heads/main/licenses.txt"


def get_hwid():

    data = (
        platform.node() +
        platform.system() +
        platform.processor()
    )

    return hashlib.sha256(
        data.encode()
    ).hexdigest()


HWID = get_hwid()
print(HWID)
try:

    data = requests.get(
        LICENSE_URL
    ).text.splitlines()

    found = False

    for line in data:

        line = line.strip()

        if not line:
            continue

        if "|" not in line:
            continue

        hwid, expire = line.split("|", 1)

        if hwid == HWID:

            found = True

            expire_date = datetime.strptime(
                expire,
                "%Y-%m-%d"
            )

            now = datetime.now()

            if now > expire_date:

                print("❌ License expired")

                sys.exit()

            days = (
                expire_date - now
            ).days

            print(
                f"✅ License active "
                f"({days} days)"
            )

            break

    if not found:

        print("❌ HWID not found")

        sys.exit()

except Exception as e:

    print("❌ License server error")

    print(e)

    sys.exit()
import os
import json

CONFIG_FILE = "config.json"


def load_config():

    if os.path.exists(CONFIG_FILE):

        with open(CONFIG_FILE, "r") as f:

            return json.load(f)

    api_id = input("API ID: ")

    api_hash = input("API HASH: ")

    data = {
        "api_id": int(api_id),
        "api_hash": api_hash
    }

    with open(CONFIG_FILE, "w") as f:

        json.dump(data, f)

    return data


config = load_config()

api_id = config["api_id"]

api_hash = config["api_hash"]
from telethon import TelegramClient, events
import importlib.util
import asyncio
import os
import sys
import time
import random
from deep_translator import GoogleTranslator
import requests


bot = TelegramClient(
    "userbot",
    api_id,
    api_hash
	)

start_time = time.time()

MODULES_DIR = "modules"

if not os.path.exists(MODULES_DIR):
    os.mkdir(MODULES_DIR)

loaded_modules = {}

modules = {
    "Core": [
        "ping",
        "help",
        "info",
        "lm",
        "ulm",
        "modules",
        "restart"
    ],

    "Fun": [
        "iq",
        "gay",
        "hack"
    ]
}

loaded_modules = {}

module_commands = {}

def load_module(path):

    name = os.path.basename(path).replace(".py", "")

    spec = importlib.util.spec_from_file_location(
        name,
        path
    )

    module = importlib.util.module_from_spec(spec)

    sys.modules[name] = module

    spec.loader.exec_module(module)

    loaded_modules[name] = module

    if hasattr(module, "commands"):

        module_commands[name] = module.commands

    if hasattr(module, "register"):

        module.register(bot)

    return name

@bot.on(events.NewMessage(pattern=r"\.ping"))
async def ping(event):

    start = time.time()

    await event.edit("🏓 Pong...")

    end = round((time.time() - start) * 1000)

    await event.edit(
        f"🏓 Pong: `{end}ms`"
    )
import os
import sys
@bot.on(events.NewMessage(pattern=r"\.stop"))
async def stop_cmd(event):

    await event.edit(
        "🛑 Termux closed"
    )

    await bot.disconnect()

    os.system("pkill -f com.termux")

    sys.exit()

AFK = False
AFK_REASON = ""

@bot.on(events.NewMessage(pattern=r"\.afk ?(.*)"))
async def afk_handler(event):

    global AFK
    global AFK_REASON

    AFK = True
    AFK_REASON = event.pattern_match.group(1)

    text = "🌙 AFK режим включен"

    if AFK_REASON:
        text += f"\n📝 Причина: {AFK_REASON}"

    await event.edit(text)

from gtts import gTTS


@bot.on(events.NewMessage(pattern=r"\.weather (.+)"))
async def weather_handler(event):

    city = event.pattern_match.group(1)

    try:

        msg = await event.edit(
            "🌦 Загрузка..."
        )

        url = f"https://wttr.in/{city}?format=3"

        weather = requests.get(url).text

        await msg.edit(weather)

    except Exception as e:

        await event.edit(
            f"❌ Error: {e}"
        )



@bot.on(events.NewMessage(pattern=r"\.wiki (.+)"))
async def wiki_handler(event):

    query = event.pattern_match.group(1)

    try:

        msg = await event.edit(
            "📚 Поиск..."
        )

        query_encoded = quote(query)

        url = (
            "https://ru.wikipedia.org/api/rest_v1/page/summary/"
            f"{query_encoded}"
        )

        response = requests.get(url)

        if response.status_code != 200:

            return await msg.edit(
                "❌ Не найдено"
            )

        data = response.json()

        text = data.get("extract")

        if not text:

            return await msg.edit(
                "❌ Нет информации"
            )

        await msg.edit(
            f"📚 {query}\n\n{text[:3500]}"
        )

    except Exception as e:

        await event.edit(
            f"❌ Error: {e}"
        )

@bot.on(events.NewMessage(incoming=True))
async def afk_reply(event):

    global AFK

    if AFK and event.is_private:

        text = "🌙 Я сейчас AFK"

        if AFK_REASON:
            text += f"\n📝 {AFK_REASON}"

        await event.reply(text)

import yt_dlp
import os

@bot.on(events.NewMessage(pattern=r"\.mus (.+)"))
async def music_handler(event):

    query = event.pattern_match.group(1)

    msg = await event.reply(
        "🎵 Поиск музыки..."
    )

    try:

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "song.%(ext)s",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                f"ytsearch:{query}",
                download=True
            )["entries"][0]

            file_name = ydl.prepare_filename(info)

        await bot.send_file(
            event.chat_id,
            file_name,
            caption=f"🎵 {info['title']}"
        )

        os.remove(file_name)

        await msg.delete()

    except Exception as e:

        await msg.edit(
            f"❌ Error: {e}"
        )

@bot.on(events.NewMessage(pattern=r"\.img (.+)"))
async def image_handler(event):

    prompt = event.pattern_match.group(1)

    try:

        msg = await event.edit(
            "🎨 Генерация..."
        )

        url = f"https://image.pollinations.ai/prompt/{prompt}"

        response = requests.get(url)

        file_name = "image.jpg"

        with open(file_name, "wb") as f:
            f.write(response.content)

        await bot.send_file(
            event.chat_id,
            file_name,
            caption=f"🖼 Prompt: {prompt}"
        )

        os.remove(file_name)

        await msg.delete()

    except Exception as e:

        await event.edit(
            f"❌ Error: {e}"
        )

@bot.on(events.NewMessage(pattern=r"\.reload"))
async def reload_cmd(event):

    global loaded_modules
    global module_commands

    loaded_modules.clear()

    module_commands.clear()

    for file in os.listdir(MODULES_DIR):

        if file.endswith(".py"):

            try:

                load_module(
                    os.path.join(
                        MODULES_DIR,
                        file
                    )
                )

            except Exception as e:

                print(e)

    await event.edit(
        "🔄 Modules reloaded"
    )

@bot.on(events.NewMessage(pattern=r"\.tr (.+)"))
async def translate_handler(event):

    text = event.pattern_match.group(1)

    try:

        translated = GoogleTranslator(
            source='auto',
            target='ru'
        ).translate(text)

        await event.reply(f"🌍 Перевод:\n\n{translated}")

    except Exception as e:
        await event.reply(f"❌ Error: {e}")

@bot.on(events.NewMessage(pattern=r"\.restart"))
async def restart_cmd(event):

    await event.edit(
        "🔄 Restarting..."
    )


@bot.on(events.NewMessage(pattern=r"\.(help|знал)"))
async def help_cmd(event):

    text = """
🌘 Bro9ibotfree 🌘

⚡
 ping    .ping
 help    .help
 info    .info
 restart .restart
 lm      .lm
 ulm     .ulm
 reload  .reload
 iq      .iq
 gay     .gay
 hack    .hack
 img     .img
 mus     .mus
 tr      .tr
afk     .afk
wiki    .wiki
"""

    if module_commands:

        text += "\n📦 Modules:\n\n"

        for mod, cmds in module_commands.items():

            text += (
                f"▫️ {mod}: "
                f"( {' | '.join(cmds)} )\n"
            )

    await event.edit(text)

@bot.on(events.NewMessage(pattern=r"\.info"))
async def info(event):

    me = await bot.get_me()

    uptime = int(time.time() - start_time)

    text = f"""
╔═══ 🌘 bro9iBOT INFO 🌘 ═══╗

👤 {me.first_name}
🆔 {me.id}
📦Модули: {len(loaded_modules)}
⏳Время Запуска: {uptime}s
👤Роль : FREE⏳
╚═════════════════════╝
"""
    photos = await bot.get_profile_photos(
        me.id,
        limit=1
    )

    if photos:

        await bot.send_file(
            event.chat_id,
            photos[0],
            caption=text
        )

        await event.delete()

    else:

        await event.edit(text)


@bot.on(events.NewMessage(pattern=r"\.lm"))
async def loadmod(event):

    reply = await event.get_reply_message()

    if not reply:
        return await event.edit(
            "❌ Reply to .py file"
        )

    if not reply.file:
        return await event.edit(
            "❌ File not found"
        )

    file_name = reply.file.name

    path = await reply.download_media(
        file=f"modules/{file_name}"
    )

    try:

        module_name = load_module(path)

        await event.edit(
            f"✅ Loaded: {module_name}"
        )

    except Exception as e:

        await event.edit(
            f"❌ {e}"
                )


@bot.on(events.NewMessage(pattern=r"\.modules"))
async def modules_cmd(event):

    text = "📦 Loaded modules:\n\n"

    if not loaded_modules:

        text += "No modules loaded"

    else:

        for mod in loaded_modules:
            text += f"▫️ `{mod}`\n"

    await event.edit(text)


@bot.on(events.NewMessage(pattern=r"\.iq"))
async def iq(event):

    iq = random.randint(1, 300)

    await event.edit(
        f"🧠 IQ: `{iq}`"
    )


@bot.on(events.NewMessage(pattern=r"\.gay"))
async def gay(event):

    gay = random.randint(1, 100)

    await event.edit(
        f"🏳️‍🌈 ГЕЙ ЛЕВЕЛ: `{gay}%`"
    )


@bot.on(events.NewMessage(pattern=r"\.hack"))
async def hack(event):

    await event.edit(
        "💻 Hacking..."
    )

    steps = [
        "Connecting to Telegram...",
        "Bypassing security...",
        "Injecting malware...",
        "Downloading data...",
        "Done ✅"
    ]

    for step in steps:

        await asyncio.sleep(1)

        await event.edit(
            f"💻 {step}"
        )

bot.start()
print("😈Готово Заходи в ТГ😈")
bot.run_until_disconnected()

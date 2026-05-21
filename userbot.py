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
        "modules"
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

@bot.on(events.NewMessage(pattern=r"\.ping"))
async def ping(event):

    start = time.time()

    await event.edit("🏓 Pong...")

    end = round((time.time() - start) * 1000)

    await event.edit(
        f"🏓 Pong: `{end}ms`"
    )


@bot.on(events.NewMessage(pattern=r"\.(help|знал)"))
async def help_cmd(event):

    text = """
🌘 USERBOT HELP

⚡ Main:
.ping
.help
.info

🎲 Fun:
.iq
.gay
.hack
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
   Player Menu
👤 Nick: {me.first_name}
🆔 ID: {me.id}
⚡ Status: Online
📦 Modules: {len(loaded_modules)}
⏳ Uptime: {uptime}s
👤   bro9i UserBot

╚═══════════════════════╝
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
        f"🏳️‍🌈 Gay level: `{gay}%`"
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


print("🌘бот запущен🌘")

bot.start()

bot.run_until_disconnected()

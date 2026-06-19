from telethon import TelegramClient, events
import json
import os

api_id = 37789635
api_hash = "fdb91993189c49f83798fd293de096d0"
bot_token = "8950484176:AAF7Vko4XBUgp_VFkBlEii3j3uPWBwMzra8"

user_client = TelegramClient("session", api_id, api_hash)
bot_client = TelegramClient("bot", api_id, api_hash)

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump({
            "sources": [],
            "target": "",
            "enabled": True
        }, f, indent=4)


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


@bot_client.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        "الأوامر:\n"
        "/addsource رابط_القناة\n"
        "/settarget رابط_القناة\n"
        "/listsources\n"
        "/delsource رابط_القناة\n"
        "/deltarget\n"
        "/stop\n"
        "/run"
    )


@bot_client.on(events.NewMessage(pattern="/addsource"))
async def add_source(event):
    config = load_config()

    try:
        source = event.raw_text.split(" ", 1)[1]
    except IndexError:
        await event.reply("اكتب رابط القناة بعد الأمر")
        return

    if source not in config["sources"]:
        config["sources"].append(source)
        save_config(config)

    await event.reply("تمت إضافة المصدر")


@bot_client.on(events.NewMessage(pattern="/settarget"))
async def set_target(event):
    config = load_config()

    try:
        target = event.raw_text.split(" ", 1)[1]
    except IndexError:
        await event.reply("اكتب رابط القناة الهدف")
        return

    config["target"] = target
    config["enabled"] = True
    save_config(config)

    await event.reply("تم تحديد الهدف")


@bot_client.on(events.NewMessage(pattern="/listsources"))
async def list_sources(event):
    config = load_config()

    if config["sources"]:
        await event.reply("\n".join(config["sources"]))
    else:
        await event.reply("لا توجد مصادر")


@bot_client.on(events.NewMessage(pattern="/delsource"))
async def del_source(event):
    config = load_config()

    try:
        source = event.raw_text.split(" ", 1)[1]
    except IndexError:
        await event.reply("اكتب رابط القناة المراد حذفها")
        return

    if source in config["sources"]:
        config["sources"].remove(source)
        save_config(config)

    await event.reply("تم حذف المصدر")


@bot_client.on(events.NewMessage(pattern="/deltarget"))
async def del_target(event):
    config = load_config()
    config["target"] = ""
    save_config(config)

    await event.reply("تم حذف الهدف")


@bot_client.on(events.NewMessage(pattern="/stop"))
async def stop_copy(event):
    config = load_config()
    config["enabled"] = False
    save_config(config)

    await event.reply("تم إيقاف النسخ")


@bot_client.on(events.NewMessage(pattern="/run"))
async def run_copy(event):
    config = load_config()
    config["enabled"] = True
    save_config(config)

    await event.reply("تم تشغيل النسخ")


@user_client.on(events.NewMessage)
async def handler(event):
    config = load_config()

    if not config.get("enabled", True):
        return

    if not config["target"]:
        return

    chat = await event.get_chat()
    username = getattr(chat, "username", None)

    if username:
        source = "https://t.me/" + username

        if source in config["sources"]:
            await user_client.send_message(
                config["target"],
                event.message
            )


async def main():
    await user_client.start()
    await bot_client.start(bot_token=bot_token)

    print("Bot Running...")

    await bot_client.run_until_disconnected()


with user_client:
    user_client.loop.run_until_complete(main())

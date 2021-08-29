import os

from instaloader import Instaloader, Post, Profile
from instaloader.exceptions import (BadResponseException,
                                    ProfileNotExistsException)
from pyrogram import Client, filters, idle
from pyrogram.errors.exceptions import UserNotParticipant
from pyrogram.raw.functions.bots import SetBotCommands
from pyrogram.raw.types import BotCommand
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            InputMediaPhoto, InputMediaVideo, Message)

from config import Config
from database import Data

if os.path.exists("downloads"):
    print("Download Path Exist")
else:
    os.mkdir("downloads")
    print("Download Path Created")


app = Client("instagram-bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN)


cmd = [
    BotCommand(command="start", description="Restarts The Bot"),
    BotCommand(command="help", description="Help Menu"),
    BotCommand(command="post", description="(Long Press) Download Post"),
    BotCommand(command="story", description="(Long Press) Download Story"),
    BotCommand(command="dp", description="(Long Press) Download Profile Picture")
]


cmd_data = SetBotCommands(commands=cmd)


insta = Instaloader()

def joined():

    def decorator(func):

        async def wrapped(client, message : Message):

            try:
                check = await app.get_chat_member("SJ_Bots", message.from_user.id)
                if check.status in ['member','administrator','creator']:
                    await func(client, message)
                else:
                    await message.reply("💡 You must join our channel in order to use this bot",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("JOIN CHANNEL", url="https://t.me/SJ_Bots")]]))
            except UserNotParticipant as e:
                await message.reply("💡 You must join our channel in order to use this bot",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("JOIN CHANNEL", url="https://t.me/SJ_Bots")]]))

        return wrapped

    return decorator

@app.on_message(filters.command("start"))
@joined()
async def start(client, message : Message):
    await message.reply(f"Hello, {message.from_user.username}\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        "This is SJ Insta Bot. This Bot Can Fetch instagram Posts, Stories, anf Profile Pictures\n"
                        "𝗨𝘀𝗲 /help to know more\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        "✅𝗖𝗥𝗘𝗗𝗜𝗧𝗦:- @SJ_Bots\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n")
    
    check = await Data.is_in_db(message.from_user.id)
    if check == False:
        await Data.add_new_user(message.from_user.id)


@app.on_message(filters.command("help"))
@joined()
async def help(client, message : Message):
    await message.reply("**HELP MENU**\n\n"
                        "/start - Restarts The Bot\n"
                        "/help - Send This Help Menu\n\n"
                        "/post <Post Link> - Download Post\n"
                        "/story <username> - Download Story\n"
                        "/dp <username> - Download Profile Picture\n\n"
                        "✅𝗖𝗥𝗘𝗗𝗜𝗧𝗦:- @SJ_Bots\n")


@app.on_message(filters.command("stats"))
async def stats(client, message : Message):
    count = await Data.count_users()
    await message.reply(f"**STATS**\nTotal Users : {count}")


@app.on_message(filters.command("broadcast") & filters.reply)
async def stats(client, message : Message):
    users = await Data.get_user_ids()
    tmsg = message.reply_to_message.text.markdown

    msg = await message.reply("Broadcast started")

    fails = 0
    success = 0

    for user in users:
        try:
            await app.send_message(int(user), tmsg)
            success += 1
        except:
            fails += 1

        quotient = (fails + success)/len(users)
        percentage = float(quotient * 100)
        await msg.edit(f"**Broadcast started**\n\nTotal Users : {len(users)}\nProgress : {percentage} %")

    await msg.edit(f"Broadcast Completed**\n\nTotal Users : {len(users)}\nSuccess : {success}\nFails : {fails}")


@app.on_message(filters.command("post"))
@joined()
async def post_download(client, message : Message):
    msg = await message.reply("Processing...")
    try:
        url = message.command[1]
    except IndexError:
        await msg.edit("Please provide a link to download posts after /post\nUse /help for more details")
        return

    try:
        insta.login(user="unknown.s.mac", passwd="Sohag@02")
        a = url.replace("https://www.instagram.com/p/", "")
        b = a.split("/")
        post_id = b[0]#url#a[ : 11]
        post = Post.from_shortcode(insta.context, post_id)
        insta.download_post(post, "downloads")

        list = os.listdir("downloads")
        path = ""
        for file in list:
            if file.endswith(".jpg"):
                path = f"downloads\{file}"
                break
            else:
                continue


        await message.reply_document(path, caption="Here is the post")
        await msg.delete()


        for file in os.listdir("downloads"):
            os.remove(f"downloads/{file}")
    except BadResponseException: 
        await msg.edit("The post link is invalid")
    except:
        raise

@app.on_message(filters.command("dp"))
@joined()
async def dp_download(client, message : Message):
    try:
        u = message.command[1]
    except IndexError:
        await message.reply("Please send a username after /post\nUse /help to know more")
        return

    await message.reply("Processing...")

    if "https://www.instagram.com/" in u:
        a = u.replace("https://www.instagram.com/", "")
        username = a.replace("/", "")
    elif "@" in u:
        username = u.replace("@")
    else:
        username = u

    try:
        insta.download_profile(username, profile_pic_only=True)
    except ProfileNotExistsException:
        await message.reply("No such Profile Found")
        return

    list = os.listdir(username)
    path = ""
    for file in list:
        if file.endswith(".jpg"):
            path = f"{username}\{file}"
            break
        else:
            continue

    await message.reply_document(path, caption=f"Here is the Profile Picture of {username}")

    for file in list:
        os.remove(f"{username}/{file}")

    os.rmdir(username)



@app.on_message(filters.command("story"))
@joined()
async def story_download(client, message : Message):
    msg = await message.reply("Processing...")
    try:
        u = message.command[1]
    except IndexError:
        await msg.edit("Please send a username after /story\nUse /help to know more")
        return

    if "https://www.instagram.com/" in u:
        a = u.replace("https://www.instagram.com/", "")
        username = a.replace("/", "")
    elif "@" in u:
        username = u.replace("@")
    else:
        username = u

    insta.login(user="unknown.s.mac", passwd="Sohag@02")
    profile = Profile.from_username(insta.context, username)

    folder = f"{profile.username}"
    insta.download_stories(userids=[profile.userid],filename_target=folder)

    files = os.listdir(folder)

    photos = []
    for story in files:
        if story.endswith(".jpg"):
            photos.append(InputMediaPhoto(f"{folder}/{story}"))
        elif story.endswith(".mp4"):
            photos.append(InputMediaVideo(f"{folder}/{story}"))


    await message.reply_media_group(photos)
    await msg.delete()

    for file in files:
        os.remove(f"{folder}/{file}")

    os.rmdir(folder)



@app.on_message(filters.command("cc"))
async def sen(client, message : Message):
    for file in os.listdir("downloads"):

        os.remove(file)


async def run_bot():
    await app.start()
    await app.send(cmd_data)
    print("Bot Started")
    await idle()


app.loop.run_until_complete(run_bot())

# app.run()  
# app.send(cmd_data)



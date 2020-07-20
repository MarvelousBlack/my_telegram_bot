#!/usr/bin/env python3

# Copyright (C) 2020 megumifox <i@megumifox.com>

from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.channels import EditPhotoRequest
from telethon.tl.types import InputChatUploadedPhoto
from PIL import Image, ImageSequence 
from datetime import datetime, timedelta, timezone
import logging
import os
import cv2
import asyncio
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)
logger=logging.getLogger("AVATAR")
api_id = 
api_hash = ''
bot_token = ''
chat_list = []

client = TelegramClient('avatar_bot',
                    api_id,
                    api_hash,
                    )
client.start(bot_token=bot_token)

last_all = []

avatar_lock = asyncio.Lock()

async def is_timeup(event):
    global last_all
    for chat in last_all:
        if chat['chat_id'] == event.chat_id:
            last = chat['last']
            if (event.message.date - last) < timedelta(seconds = 100):
                t = (timedelta(seconds = 100) - (event.message.date -last)).total_seconds()
                m = await event.reply("賢者時間還剩"+str(t)+"s")
                return False
            else:
                return True
    last = datetime.now(timezone.utc) - timedelta(hours = 2)
    dictadd = {'chat_id': event.chat_id, 'last': last}
    last_all.append(dictadd)
    return True

def update_last(event):
    global last_all
    for chat in last_all:
        if chat['chat_id'] == event.chat_id:
           chat['last'] = event.message.date
    return None

def conv_sticker(file):
    im = Image.open(file).convert("RGBA")
    im.save("/tmp/avatar.png","png")
    os.remove(file)

def conv_gif(file):
    im = Image.open(file)
    iter = ImageSequence.Iterator(im)
    iter[2].save('/tmp/avatar.png')
    os.remove(file)

def conv_mp4(file):
    try:
        videoCapture = cv2.VideoCapture(file)
        success, frame = videoCapture.read()
        cv2.imwrite('/tmp/avatar.png',frame)
    finally:
        videoCapture.release()
        os.remove(file)

def img2png(file):
    im = Image.open(file).convert("RGBA")
    im.save("/tmp/avatar.png","png")
    os.remove(file)

def conv_white(file):
    im = Image.open(file).convert("RGBA")
    wbg = Image.new("RGBA", im.size,color=(255,255,255,255))
    wbg = Image.alpha_composite(wbg, im)
    wbg.save(file)

def size2small(file):
    im = Image.open(file).convert("RGBA")
    x,y = im.size
    return (x < 160 or y < 160)

async def avatar(event,white=False):
    sender = await event.get_sender()
    logger.info("sender_id = %s,username= %s,sender first_name = %s,last_name=%s, message = %s,chat_id= %s",event.message.from_id,sender.username,sender.first_name,sender.last_name,event.message.message ,event.chat_id)

    global chat_list
    if event.chat_id not in chat_list:
        m = await event.reply("如果需要使用請先聯系 @MarvelousBlack 將該羣加入白名單。chat_id={}".format(event.chat_id))
        return None

    async with avatar_lock:
        if not await is_timeup(event):
            return None
        replymsg = await event.message.get_reply_message()
        try:
            if  replymsg.file is not None:
                if replymsg.file.size > 5*1024**2:
                    m = await event.reply("不要啊啊啊啊，太大了！！！")
                    return None
                if replymsg.file.name == "sticker.webp":
                    file_name = '/tmp/sticker.webp'
                    await client.download_media(message=replymsg,file=file_name)
                    conv_sticker(file_name)
                elif replymsg.file.mime_type == "video/mp4":
                    file_name = '/tmp/video.mp4'
                    await client.download_media(message=replymsg,file=file_name)
                    conv_mp4(file_name)
                elif replymsg.file.mime_type == "image/gif":
                    file_name = '/tmp/noirgif.gif'
                    await client.download_media(message=replymsg,file=file_name)
                    conv_gif(file_name)
                elif "image" in replymsg.file.mime_type:
                    file_name = '/tmp/image'+ replymsg.file.ext
                    await client.download_media(message=replymsg,file=file_name)
                    img2png(file_name)
                else:
                    m = await event.reply("不支持的類型")
                    return None
    
            if white:
                conv_white('/tmp/avatar.png')
            if size2small('/tmp/avatar.png'):
                os.remove('/tmp/avatar.png')
                m = await event.reply("你的頭太小了！需要 160×160 以上")
                return None
    
            upload_file_result = await client.upload_file(file='/tmp/avatar.png')
            os.remove('/tmp/avatar.png')
            input_chat_uploaded_photo = InputChatUploadedPhoto(upload_file_result)
            result = await client(EditPhotoRequest(channel=event.message.to_id,
            photo=input_chat_uploaded_photo))
            update_last(event)
            logger.info("success,chat_id = %s",event.chat_id)
        except BaseException:
            m = await event.reply("你的頭呢？")
    return None


@client.on(events.NewMessage(func=lambda e: not e.is_private,pattern=r'/avatar_black'))
async def handler(event):
     await avatar(event)

@client.on(events.NewMessage(func=lambda e: not e.is_private,pattern=r'/avatar_white'))
async def handler(event):
    await avatar(event,white=True)

@client.on(events.NewMessage(pattern=r'/start'))
async def handler(event):
    m = await event.reply("如果需要使用請先聯系 @MarvelousBlack，如果已經在使用請忽略本消息。關於信息在 info 裏。")

@client.on(events.NewMessage(pattern=r'/info'))
async def handler(event):
    m = await event.reply(u"本機器人提供羣組換頭功能，支持視頻，GIF,表情和正常的圖片(不支持動態表情)。\n 用法爲引用需要更換的消息（消息中包含圖片視頻等）然後使用 avatar 命令\n 黑白之間的區別是對透明圖片背景色的處理。 \n Source code: https://github.com/MarvelousBlack/my_telegram_bot/tree/master/avatar")

if __name__ == "__main__":
    try:
        print('(Press Ctrl+C to stop this)')
        client.run_until_disconnected()
    finally:
        client.disconnect()


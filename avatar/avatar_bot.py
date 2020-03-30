from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.channels import EditPhotoRequest
from telethon.tl.types import InputChatUploadedPhoto
from PIL import Image, ImageSequence 
from datetime import datetime, timedelta, timezone
import logging
import os
import cv2
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.ERROR)
api_id = 
api_hash = ''
bot_token = ''
your_channel_id =

client = TelegramClient('avatar_bot',
                    api_id,
                    api_hash,
                    )
client.start(bot_token=bot_token)


channel_entity = client.get_entity(PeerChannel(channel_id=your_channel_id))
last = datetime.now(timezone.utc) - timedelta(hours = 2)

def conv_sticker(file):
    im = Image.open(file).convert("RGB")
    im.save("/tmp/sticker.jpg","jpeg")
    os.remove(file)

def conv_gif(file):
    im = Image.open(file)
    iter = ImageSequence.Iterator(im)
    iter[2].save('/tmp/noirgif.png')
    os.remove(file)

def conv_mp4(file):
    try:
        videoCapture = cv2.VideoCapture(file)
        success, frame = videoCapture.read()
        cv2.imwrite('/tmp/video.png',frame)
    finally:
        videoCapture.release()
        os.remove(file)

@client.on(events.NewMessage(chats=channel_entity,pattern=r'/avatar'))
async def handler(event):
    global last
    if (event.message.date - last) < timedelta(seconds = 100):
        t = (timedelta(seconds = 100) - (event.message.date -last)).total_seconds()
        m = await event.reply("賢者時間還剩"+str(t)+"s")
        return None
    replymsg = await event.message.get_reply_message()
    try:
        if replymsg.file is not None:
            if replymsg.file.size > 5*1024**2:
                m = await event.reply("不要啊啊啊啊，太大了！！！")
                return None
            if replymsg.file.name == "sticker.webp":
                file_name = '/tmp/sticker.webp'
                await client.download_media(message=replymsg,file=file_name)
                conv_sticker(file_name)
                upload_file_result = await client.upload_file(file='/tmp/sticker.jpg')
                os.remove('/tmp/sticker.jpg')
            elif replymsg.file.mime_type == "video/mp4":
                file_name = '/tmp/video.mp4'
                await client.download_media(message=replymsg,file=file_name)
                conv_mp4(file_name)
                upload_file_result = await client.upload_file(file='/tmp/video.png')
            elif replymsg.file.mime_type == "image/gif":
                file_name = '/tmp/noirgif.gif'
                await client.download_media(message=replymsg,file=file_name)
                conv_gif(file_name)
                upload_file_result = await client.upload_file(file='/tmp/noirgif.png')
                os.remove('/tmp/noirgif.png')
            elif "image" in replymsg.file.mime_type:
                file_name = '/tmp/image'+ replymsg.file.ext
                await client.download_media(message=replymsg,file=file_name)
                upload_file_result = await client.upload_file(file=file_name)
                os.remove(file_name)
            else:
                m = await event.reply("不支持的類型")
                return None

        input_chat_uploaded_photo = InputChatUploadedPhoto(upload_file_result)
        result = await client(EditPhotoRequest(channel=event.message.to_id,
        photo=input_chat_uploaded_photo))
        last = event.message.date
    except BaseException:
        m = await event.reply("你的頭呢？")
    return None

try:
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
finally:
    client.disconnect()


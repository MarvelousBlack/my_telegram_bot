from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.channels import EditPhotoRequest
from telethon.tl.types import InputChatUploadedPhoto
from PIL import Image
from datetime import datetime, timedelta, timezone
import logging
import os
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
           if replymsg.file.name == "sticker.webp":
               await client.download_media(message=replymsg,file='/tmp')
               im = Image.open("/tmp/sticker.webp").convert("RGB")
               im.save("/tmp/sticker.jpg","jpeg")
               os.remove("/tmp/sticker.webp")
               upload_file_result = await client.upload_file(file='/tmp/sticker.jpg')
               input_chat_uploaded_photo = InputChatUploadedPhoto(upload_file_result)
           else:
               input_chat_uploaded_photo=replymsg.media
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


#!/usr/bin/env python3

# Copyright (C) 2020 megumifox <i@megumifox.com>

from telethon import TelegramClient, events, sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon.tl.functions.channels import EditPhotoRequest
from telethon.tl.types import InputChatUploadedPhoto
from datetime import datetime, timedelta, timezone
from pixiv import AppPixivAPI_wrap
import logging
import asyncio
import os
import re

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)
logger=logging.getLogger("pixivdownloadbot")
api_id = 
api_hash = ''
bot_token = ''
bot_name=''
_USERNAME = ""
_PASSWORD = ""
whitelist_user = []
chat_list = []
directory = "dl"
artworks_root = "https://www.pixiv.net/artworks/"
pixiv = AppPixivAPI_wrap()

client = TelegramClient(bot_name,
                    api_id,
                    api_hash,
                    )

async def pixiv_download(image_id, nsfw=True):
    logger.info("image_id:%s",image_id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    json_result = await pixiv.illust_detail(image_id)
    logger.debug(json_result)
    illust = json_result.illust
    if illust is not None:
        urls = await pixiv.getImageUrl(illust)
    else:
        raise ValueError("Cannot fetch illust")

    names = []

    if (not nsfw and ('R-18' in illust['tags'][0]['name'])):
        raise ValueError("lsp")

    for url in urls:
            url_basename = os.path.basename(url)
            name = url_basename
            logger.info("Download %s",name)
            await pixiv.download(url, path=directory, name=name)
            names.append(name)
            pixiv.randSleep()
    return names,illust.title

@client.on(events.NewMessage(pattern=r'/start'))
async def handler(event):
    if '@' in event.message.message and not event.message.mentioned and bot_name not in event.message.message:
        return 0
    m = await event.reply("link start")

@client.on(events.NewMessage(func=lambda e: e.is_private))
async def handler(event):
    if event.sender_id not in whitelist_user:
        m = await event.reply("=.=")
        return None
    else:
        image_ids = re.findall('(\d+)',event.message.message)
        logger.debug(image_ids)
        if image_ids == []:
            return 0
        mr = await event.reply("Downloading ...")
        for image_id in image_ids:
            if len(image_id) > 5:
                try:
                    picnames,title = await pixiv_download(int(image_id))
                    for picname in picnames:
                        m = await event.reply("title: {}\nfilename: {}\npixiv_id: [{}]({})".format(title,picname,image_id,artworks_root+image_id),force_document=True,file=os.path.join(directory,picname))
                except BaseException as e:
                    logger.error(e)
                    m = await event.reply("´_>`, {}".format(e))
        await mr.delete()

@client.on(events.NewMessage(func=lambda e: not e.is_private,pattern=r'/pixiv_id'))
async def handler(event):
        if event.chat_id not in chat_list:
            m = await event.reply("如果需要使用請先聯系 @MarvelousBlack 將該羣加入白名單。chat_id={}".format(event.chat_id))
            return None
        image_ids = re.findall('(\d+)',event.message.message)
        logger.debug(image_ids)
        if image_ids == []:
            m = await event.reply("找不到圖片id")
            return 0
        mr = await event.reply("Downloading ...")
        for image_id in image_ids:
            if len(image_id) > 5:
                try:
                    picnames,title = await pixiv_download(int(image_id), nsfw=False)
                    for picname in picnames:
                        m = await event.reply("title: {}\nfilename: {}\npixiv_id: [{}]({})".format(title,picname,image_id,artworks_root+image_id),force_document=False,file=os.path.join(directory,picname))
                        if 'p1' in picname:
                            break
                except BaseException as e:
                    logger.error(e)
                    m = await event.reply("´_>`, {}".format(e))
        await mr.delete()
            

async def main():
    await pixiv.login(_USERNAME, _PASSWORD)
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        client.start(bot_token=bot_token)
        asyncio.get_event_loop().run_until_complete(main())
    except:
        pass
    finally:
        client.disconnect()


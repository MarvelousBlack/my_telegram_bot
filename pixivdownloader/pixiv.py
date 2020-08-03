#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2020 megumifox <i@megumifox.com>

import asyncio
import os
import random
import time
from pixivpy_async import AppPixivAPI, PixivError
import datetime
import logging
from functools import wraps
import aiohttp

MAX_RETRIES = 5

logger=logging.getLogger("pixiv")

def retry(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        for _ in range(1, MAX_RETRIES + 1):
            try:
                return await f(*args, **kwargs)
            except aiohttp.ServerConnectionError:
                pass
    return wrapper

def always_retry(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        while True:
            try:
                return await f(*args, **kwargs)
            except aiohttp.ServerConnectionError:
                pass
    return wrapper


class AppPixivAPI_wrap(AppPixivAPI):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_auth = datetime.datetime.fromtimestamp(0)
        self.username = ""
        self.password = ""
        self.TOKEN_LIFESPAN = datetime.timedelta(seconds=3600)

    @always_retry
    async def login(self, username, password):
        self.password = password
        self.username = username
        await super().login(username, password)
        self.last_auth = datetime.datetime.now()
        logger.info('Pixiv login done')
        return self  # allows chaining

    def randSleep(self, base=0.1, rand=0.5):
        time.sleep(base + rand*random.random())

    async def getImageUrl(self, illust, square=False):
        if square:
            return [illust['image_urls']['square_medium'],]
        else:
            if illust['meta_single_page'] != {}:
                return [illust['meta_single_page']['original_image_url'],]
            else:
                urls = []
                for meta_page in illust.meta_pages:
                    urls.append(meta_page['image_urls']['original'])
                return urls

    async def reauth(self):
        """Re-authenticates with pixiv if the last login was more than TOKEN_LIFESPAN ago"""
        if datetime.datetime.now() - self.last_auth > self.TOKEN_LIFESPAN:
            try:
                await self.login(self.username, self.password)
            except PixivError:
                raise
            else:
                logger.debug("Reauth successful")
                self.last_auth = datetime.datetime.now()

    @retry
    async def illust_detail(self, illust_id, req_auth=True):
        await self.reauth()
        return await super().illust_detail(illust_id, req_auth)

    @retry
    async def download(self,image_url,path,name):
        await self.reauth()
        return await super().download(image_url,path=path,name=name)



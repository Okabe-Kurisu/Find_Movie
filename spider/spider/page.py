# -*- coding: utf-8 -*-
# @Time    : 2018/10/1 11:23
# @Author  : Amadeus
# @Desc : 用来下载页面
import asyncio
from aiohttp import ClientSession

from spider import spider_config, proxy


async def download(url, param=None):
    while True:
        proxies = proxy.get_proxy()
        try:
            async with ClientSession(cookies=spider_config.get_cookie(), headers=spider_config.get_header()) as session:
                async with session.get(url, params=param,
                                       proxy="http://{}:{}".format(proxies[0], proxies[1]),
                                       timeout=3) as r:
                    text = await r.text()
                    if r.status == 404:
                        return
                    assert r.status == 200
                    await asyncio.sleep(1)
                    return text
        except Exception:
            proxy.bad_proxy(proxies)
            continue
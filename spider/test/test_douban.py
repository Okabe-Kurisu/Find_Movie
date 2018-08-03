import asyncio
from json import JSONDecodeError

from aiohttp import ClientOSError, ClientHttpProxyError
from concurrent.futures._base import TimeoutError
from spider.douban import Douban

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    douban = Douban()
    while True:
        json = ""
        try:
            print("http://" + str(douban.proxy[0]) + ":" + str(douban.proxy[1]))
            json = loop.run_until_complete(douban.get_tpye_list())
            loop.run_until_complete(douban.get_subject(json))
        except Exception:  # 如果被停止了连接
            print("豆瓣太狡猾")
            douban.init()
    loop.close()

import asyncio
import traceback

from aiohttp import ClientOSError

from spider.douban import Douban
from util import proxy

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    douban = Douban()
    while True:
        json = ""
        try:
            p = loop.run_until_complete(proxy.get_proxy())
            douban.init(p)
            print(douban.get_params())
            json = loop.run_until_complete(douban.get_tpye_list())
        except ClientOSError:  # 如果被停止了连接
            traceback.print_exc()
            loop.run_until_complete(proxy.del_proxy(douban.proxy[0]))
            p = loop.run_until_complete(proxy.get_proxy())
            douban.init(p)
        print(json)
    loop.close()

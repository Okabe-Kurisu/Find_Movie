import multiprocessing, sys

import asyncio
import traceback

from aiohttp.client_exceptions import ClientResponseError, ClientOSError, ServerDisconnectedError, ClientPayloadError
from sql.redisHelper import RedisHelper
from IPProxyPool.IPProxy import Proxy_Pool_Start
from spider.spider import Spider
from sql.dbHelper import DBSession
from concurrent.futures._base import TimeoutError


def run():
    loop = asyncio.get_event_loop()
    session = DBSession()
    spider = Spider(session)
    while True:
        try:
            loop.run_until_complete(spider.get_tpye_list())
            loop.run_until_complete(spider.get_subject())
        except (TimeoutError, ClientResponseError, ClientOSError, ServerDisconnectedError,
                RuntimeWarning, AssertionError, ClientPayloadError):
            spider.init()
            continue
        except Exception:
            traceback.print_exc()
            spider.init()


async def worker():
    # 获取EventLoop:
    session = DBSession()
    spider = Spider(session)
    redis = RedisHelper()
    while True:
        try:
            res = redis.randomkey()
            if res is None:
                await spider.get_tpye_list()
            await spider.get_subject()
        except (TimeoutError, ClientResponseError, ClientOSError, ServerDisconnectedError,
                RuntimeWarning, AssertionError, ClientPayloadError):
            spider.init()
            continue


def run_thread(max_thread=1):
    for x in range(max_thread):
        asyncio.ensure_future(worker())

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt as e:
        print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())
        loop.stop()
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    run_thread(max_thread=5)

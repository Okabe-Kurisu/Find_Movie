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


async def consumer(debug=False):
    session = DBSession()
    spider = Spider(session)
    redis = RedisHelper()
    while True:
        try:
            res = redis.randomkey()
            if res is None:
                await asyncio.sleep(1)
            await spider.get_subject()
        except Exception:
            if debug:
                traceback.print_exc()
            continue


async def producer(debug=False):
    session = DBSession()
    spider = Spider(session)
    redis = RedisHelper()
    while True:
        res = redis.randomkey()
        if res is None:
            try:
                await spider.get_tpye_list()
            except Exception:
                if debug:
                    traceback.print_exc()
                continue


def run_thread(max_thread=1, debug=False):
    asyncio.ensure_future(producer(debug))
    for x in range(max_thread):
        asyncio.ensure_future(consumer(debug))
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())
        loop.stop()
    finally:
        loop.close()


if __name__ == "__main__":
    run_thread(max_thread=13)

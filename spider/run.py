import multiprocessing, sys

import asyncio
import time
import traceback
from aiohttp.client_exceptions import ClientResponseError, ClientOSError, ServerDisconnectedError, ClientPayloadError
from sql.redisHelper import RedisHelper
from IPProxyPool.IPProxy import Proxy_Pool_Start
from spider.spider import Spider
from sql.dbHelper import DBSession
from concurrent.futures._base import TimeoutError


def run():
    loop = asyncio.get_event_loop()
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
    spider = Spider(session)
    while True:
        res = redis.randomkey()
        if res is None:
            await asyncio.sleep(3)
            continue
        else:
            try:
                start = time.time()
                res = await spider.get_subject()
                end = time.time()
                print(res + "，共花费{}秒".format(round(end - start, 2)))
            except Exception:
                if debug:
                    spider.get_proxy()
                    traceback.print_exc()


async def producer(debug=False, threads=1):
    spider = Spider(session)
    while True:
        res = redis.dbsize()
        preload = (int(threads / 20) + 1) * 20
        if res >= preload:
            await asyncio.sleep(1)
            continue
        else:
            try:
                start = time.time()
                res = await spider.get_tpye_list()
                end = time.time()
                print(res + "，共花费{}秒".format(round(end - start, 2)))
            except Exception:
                if debug:
                    spider.get_proxy()
                    traceback.print_exc()


def run_thread(max_thread=1, debug=False):
    # asyncio.ensure_future(status())
    asyncio.ensure_future(producer(debug=debug, threads=max_thread))
    for x in range(max_thread):
        asyncio.ensure_future(consumer(debug))
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt as e:
        print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())
        loop.stop()
        loop.run_forever()
    except Exception:
        traceback.print_exc()
    finally:
        loop.close()


redis = RedisHelper()
session = DBSession()
if __name__ == "__main__":
    run_thread(max_thread=10)

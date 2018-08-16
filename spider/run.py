import multiprocessing, sys

import asyncio
import time
import traceback

from aiohttp.client_exceptions import ClientResponseError, ClientOSError, ServerDisconnectedError, ClientPayloadError
from sql.redisHelper import RedisHelper
from spider.spider import Spider
from sql.dbHelper import DBSession
from concurrent.futures._base import TimeoutError


def run():
    print(1)
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
            res = redis.randomkey()
            print(res)
            if res is not None:
                print("------------开始消费-------------")
                try:
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
            print("------------开始生产-------------")
            try:
                await spider.get_tpye_list()
            except Exception:
                if debug:
                    traceback.print_exc()
                continue
        asyncio.sleep(0.3)


def run_thread(max_thread=1, debug=False, method=0):
    # method 为0运行生产者和消费者，1只运行消费者， 2只运行生产者
    if method != 1:
        asyncio.ensure_future(producer(debug))
    if method != 2:
        for x in range(max_thread):
            asyncio.ensure_future(consumer(debug))
    loop = asyncio.get_event_loop()
    try:
        redis = RedisHelper()
        storage = 0
        while True:
            size = redis.dbsize()
            if storage != size:
                storage = size
                print("当前还有{}条数据等待存储".format(storage))
            time.sleep(1)
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    run_thread(max_thread=1, debug=True)

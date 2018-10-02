import concurrent

import asyncio
import time
import traceback
from aiohttp.client_exceptions import ClientResponseError, ClientOSError, ServerDisconnectedError, ClientPayloadError

from sql.dbHelper import DbHelper
from sql.redisHelper import RedisHelper
from spider.spider import TypeList, MovieParse
from concurrent.futures._base import TimeoutError


async def consumer(debug=False):
    while True:
        res = redis.set_size("pages")
        if not res:
            await asyncio.sleep(1)
            continue
        else:
            try:
                start = time.time()
                m = MovieParse(redis=redis)
                res = await m.get_movie()
                end = time.time()
                if res is not None:
                    print(res + "，共花费{}秒".format(round(end - start, 2)))
            except Exception:
                traceback.print_exc()


async def producer(threads=1):
    while True:
        res = redis.set_size("pages")
        preload = (threads // 20 + 1) * 20
        if res >= preload:
            await asyncio.sleep(1)
            continue
        else:
            try:
                start = time.time()
                t = TypeList(redis=redis)
                res = await t.get_tpye_list()
                end = time.time()
                print(res + "，共花费{}秒".format(round(end - start, 2)))
            except Exception:
                traceback.print_exc()


def run_thread(max_thread=1, debug=False):
    # asyncio.ensure_future(status())
    asyncio.ensure_future(producer(threads=max_thread))
    for x in range(max_thread):
        asyncio.ensure_future(consumer(debug))
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(5)
    loop.set_default_executor(executor)
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


def clean():
    redis.flush()
    d = DbHelper()
    d.drop_DB()
    d.init_DB()


redis = RedisHelper()
if __name__ == "__main__":
    start = int(redis.get("start"))
    redis.set("start", start - 200)
    # clean()
    run_thread(max_thread=100, debug=True)

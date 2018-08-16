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
            filmlist = loop.run_until_complete(spider.get_tpye_list())
            for x in range(len(filmlist)):
                film = filmlist[x]
                movie = loop.run_until_complete(spider.get_subject(film))
                loop.run_until_complete(spider.get_tags(movie, str(film['url']), x))
        except (TimeoutError, ClientResponseError, ClientOSError, ServerDisconnectedError,
                RuntimeWarning, AssertionError, ClientPayloadError):
            spider.init()
            continue
        except Exception:
            traceback.print_exc()
            spider.init()


async def get_tpye_list(spider):
    await spider.get_tpye_list()


async def get_movie(spider):
    redis = RedisHelper()
    key = redis.randomkey()
    if key is None:
        return
    film = redis.get(key)
    movie = await spider.get_subject(film)
    await spider.get_tags(movie, str(film['url']), x)


if __name__ == "__main__":
    run()
    # todo 重构成生产者-消费者模式。生产者是spider.get_tpye_list()，消费者是get_subject和get_tags

import multiprocessing, sys

import asyncio
import traceback

from aiohttp.client_exceptions import ClientResponseError, ClientOSError, ServerDisconnectedError
from multiprocessing import Value, Queue, Process

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
                RuntimeWarning, AssertionError):
            spider.init()
            continue
        except (Exception):
            traceback.print_exc()
            spider.init()
    loop.close()


if __name__ == "__main__":
    run()

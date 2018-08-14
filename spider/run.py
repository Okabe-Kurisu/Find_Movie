import multiprocessing, sys

import asyncio
import traceback

from aiohttp.client_exceptions import ClientResponseError, ClientOSError, ServerDisconnectedError

import IPProxyPool.IPProxy as IPProxy
from spider.spider import Spider
from sql.dbHelper import DBSession
from concurrent.futures._base import TimeoutError

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    session = DBSession()
    spider = Spider(session)
    while True:
        try:
            filmlist = loop.run_until_complete(spider.get_tpye_list())
            for x in range(len(filmlist)):
                film = filmlist[x]
                data = loop.run_until_complete(spider.get_subject(film, x))
                loop.run_until_complete(spider.get_tags(data, x))
        except (TimeoutError, ClientResponseError, ClientOSError, AssertionError, ServerDisconnectedError,
                RuntimeWarning):  # 如果被停止了连接
            log = open("./log", 'w', encoding='utf-8')
            traceback.print_exc()
            spider.init()
            log.close()
            continue
        except Exception:
            log2 = open("./log2", 'w', encoding='utf-8')
            traceback.print_exc()
            log2.close()
    loop.close()

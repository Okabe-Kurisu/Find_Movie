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
    log = open("./log", 'w')
    log2 = open("./log2", 'w')
    while True:
        try:
            print("http://" + str(spider.proxy[0]) + ":" + str(spider.proxy[1]))
            filmlist = loop.run_until_complete(spider.get_tpye_list())
            loop.run_until_complete(spider.get_subject(filmlist))
        except (TimeoutError, ClientResponseError, ClientOSError, AssertionError, ServerDisconnectedError,
                RuntimeWarning):  # 如果被停止了连接
            traceback.print_exc(file=log2)
            print("豆瓣太狡猾")
            spider.init()
            continue
        except Exception:
            traceback.print_exc(file=log)
            spider.init()
    log.close()
    loop.close()

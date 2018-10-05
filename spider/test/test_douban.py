import asyncio

from spider.spider import Spider
from sql.dbHelper import DBSession

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    session = DBSession()
    douban = Spider(session)
    while True:
        json = ""
        try:
            print("http://" + str(douban.proxy[0]) + ":" + str(douban.proxy[1]))
            json = loop.run_forever(douban.get_type_list())
        except Exception:  # 如果被停止了连接
            print("豆瓣太狡猾")
            douban.init()
    loop.close()

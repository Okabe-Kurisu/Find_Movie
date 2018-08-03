import asyncio, aiohttp, json

from IPProxyPool.db.DataStore import sqlhelper


# 随便取得一个代理ip
def get_proxy():
    res = sqlhelper.select(1, {"type": 0})
    return res[0][0], res[0][1]


# 如果拿到的IP不好就删了吧
def del_proxy(ip):
    res = sqlhelper.delete({'ip': ip[0]})
    return res


if __name__ == "__main__":
    print(get_proxy())

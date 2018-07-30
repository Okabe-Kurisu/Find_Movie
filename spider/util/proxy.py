import asyncio, aiohttp, json


# 随便取得一个代理ip
async def get_proxy():
    async with aiohttp.ClientSession() as session:
        params = {'count': 1, 'country': '国内'}
        async with session.get('http://localhost:8000/', params=params) as resp:
            assert resp.status == 200
            text = await resp.text()
            res = json.loads(text)
            return res[0][0]


# 如果拿到的IP不好就删了吧
async def del_proxy(ip):
    async with aiohttp.ClientSession() as session:
        params = {'ip': ip}
        async with session.get('http://localhost:8000/delete', params=params) as resp:
            assert resp.status == 200
            text = await resp.text()
            res = json.loads(text)
            return res[1]


def excute(method, ip='0.0.0.0'):
    loop = asyncio.get_event_loop()
    if method == "get":
        res = loop.run_until_complete(get_proxy())
    elif method == "del":
        res = loop.run_until_complete(del_proxy(ip))
    loop.close()
    return res


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    json = loop.run_until_complete(get_proxy())
    print(json)

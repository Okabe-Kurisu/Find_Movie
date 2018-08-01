import asyncio, aiohttp

from aiohttp import ClientSession
from util.proxy import excute

from spider import spider_config as config

base_url = 'https://movie.douban.com/'
list_url = base_url + 'j/new_search_subjects'

# 得到豆瓣搜索页面的json列表，返回
# {"directors": ["摩砂雪", "庵野秀明", "鹤卷和哉", "前田真宏"], "rate": "8.3", "cover_x": 2932,
#  "star": "40", "title": "福音战士新剧场版：Q","url": "https:\/\/movie.douban.com\/subject\/2567647\/",
#  "casts": ["林原惠美", "绪方惠美", "宫村优子", "石田彰", "三石琴乃"],
#  "cover": "https://img3.doubanio.com\/view\/photo\/s_ratio_poster\/public\/p1768906265.webp",
#  "id": "2567647","cover_y": 4025}


async def get_tpye_list(tag="", start=0, range="0,10", sort='S'):
    # 豆瓣搜索页参数列表
    params = {
        # 豆瓣的三种排序方式，T代表热度， R代表时间， S代表评价
        'sort': sort,
        # 评分范围
        'range': range,
        # 标签, 后面跟的应该是用户自定义的标签
        'tag': '电影' + tag,
        'start': start,
        # 电影类型，具体可见spider_config.py中
        'genres': '',
    }
    header = config.get_header()
    cookie = config.get_cookie()
    proxy = "http://" + excute("get")
    async with ClientSession(cookie=cookie, header=header, proxy=proxy, timeout=10) as session:
        async with session.get(list_url, params=params) as resp:
            assert await resp.status == 200
            page = resp.text()

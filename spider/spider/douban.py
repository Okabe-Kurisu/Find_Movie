import json

from aiohttp import ClientSession, ClientOSError
from lxml import etree
from spider import spider_config as config


# 得到豆瓣搜索页面的json列表，返回
# {"directors": ["摩砂雪", "庵野秀明", "鹤卷和哉", "前田真宏"], "rate": "8.3", "cover_x": 2932,
#  "star": "40", "title": "福音战士新剧场版：Q","url": "https:\/\/movie.douban.com\/subject\/2567647\/",
#  "casts": ["林原惠美", "绪方惠美", "宫村优子", "石田彰", "三石琴乃"],
#  "cover": "https://img3.doubanio.com\/view\/photo\/s_ratio_poster\/public\/p1768906265.webp",
#  "id": "2567647","cover_y": 4025}


class Douban(object):
    base_url = 'https://movie.douban.com/'
    list_url = base_url + 'j/new_search_subjects'

    # 初始化时自动得到header和cookie
    def __init__(self, proxy="", tag="", start=0, range="0,10", sort='S', genres='剧情'):
        self.header = config.get_header()
        self.cookie = config.get_cookie()
        self.proxy = proxy
        # 豆瓣搜索页参数列表
        self.tag = tag
        self.start = start
        self.range = range
        self.sort = sort
        self.genres = genres

    def get_params(self):
        params = {
            # 豆瓣的三种排序方式，T代表热度， R代表时间， S代表评价
            'sort': self.sort,
            # 评分范围
            'range': self.range,
            # 标签, 后面跟的应该是用户自定义的标签
            'tag': '电影' + self.tag,
            'start': self.start,
            # 电影类型，具体可见spider_config.py中
            'genres': self.genres,
        }
        return params

    def get_proxy(self):
        return "http://" + str(self.proxy[0]) + ':' + str(self.proxy[1])

    # 初始化cookie
    def init(self, p):
        self.cookie = config.get_cookie()
        self.header = config.get_header()
        self.proxy = p

    # 得到搜索列表页面的url
    async def get_tpye_list(self):
        async with ClientSession(cookies=self.cookie, headers=self.header) as session:
            async with session.get(self.list_url, params=self.get_params(),
                                   timeout=20) as resp:
                assert resp.status == 200
                pages = json.loads(await resp.text())['data']
                if len(pages) == 0:
                    raise RuntimeWarning("该分类已经全部获取完毕")
                else:
                    return pages

        async def get_subject(self, url):
            async with ClientSession(cookies=self.cookie, headers=self.header, timeout=10) as session:
                async with session.get(url, params=self.get_params(), proxy=self.get_proxy(), timeout=10) as resp:
                    assert await resp.status == 200
                    html = etree.parse(resp.text())
                    html.xpath()
                    # todo 解析网页

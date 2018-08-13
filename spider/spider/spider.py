import json

import asyncio
from aiohttp import ClientSession
from lxml import etree
from spider import spider_config as config
from sql.dbHelper import Movie, Filmman, Tag, Progress
from util.proxy import get_proxy, bad_proxy, good_proxy


# 得到豆瓣搜索页面的json列表，返回
# {"directors": ["摩砂雪", "庵野秀明", "鹤卷和哉", "前田真宏"], "rate": "8.3", "cover_x": 2932,
#  "star": "40", "title": "福音战士新剧场版：Q","url": "https:\/\/movie.douban.com\/subject\/2567647\/",
#  "casts": ["林原惠美", "绪方惠美", "宫村优子", "石田彰", "三石琴乃"],
#  "cover": "https://img3.doubanio.com\/view\/photo\/s_ratio_poster\/public\/p1768906265.webp",
#  "id": "2567647","cover_y": 4025}


class Spider(object):
    base_url = 'https://movie.douban.com/'
    list_url = base_url + 'j/new_search_subjects'
    api_url = 'https://api.douban.com/v2/movie/subject/'

    # 初始化时自动得到header和cookie
    def __init__(self, session, proxy="", tag="", start=0, range="0,10", sort='S', genres=0):
        self.session = session
        self.header = config.get_header()
        self.cookie = config.get_cookie()
        self.proxy = proxy
        # 豆瓣搜索页参数列表
        self.tag = tag
        self.start = start
        self.range = range
        self.sort = sort
        self.genres = genres
        self.proxy = get_proxy()

    def get_params(self):
        params = {
            # 豆瓣的三种排序方式，T代表热度， R代表时间， S代表评价
            'sort': self.sort,
            # 评分范围
            'range': self.range,
            # 标签, 后面跟的应该是用户自定义的标签
            'tags': '电影' + self.tag,
            'start': self.start,
            # 电影类型，具体可见spider_config.py中
            'genres': config.douban_type[self.genres],
        }
        return params

    def get_proxy(self):
        return "http://" + str(self.proxy[0]) + ':' + str(self.proxy[1])

    def save_progress(self, x=0):
        progress = Progress(id=1, start=self.start + x, genres=self.genres)
        progress.save(self.session)

    def load_progress(self):
        progress = Progress.load(self.session)
        if progress is None:
            return
        self.start = progress.start
        self.genres = progress.genres

    # 初始化cookie
    def init(self):
        self.cookie = config.get_cookie()
        self.header = config.get_header()
        bad_proxy(self.proxy)
        self.proxy = get_proxy()
        self.load_progress()

    # 得到搜索列表页面的url
    async def get_tpye_list(self):
        async with ClientSession(cookies=self.cookie, headers=self.header) as session:
            async with session.get(self.list_url, params=self.get_params(),
                                   proxy="http://" + str(self.proxy[0]) + ":" + str(self.proxy[1]),
                                   timeout=10) as resp:
                text = await resp.text()
                assert resp.status == 200, "失败，理由如下{}".format(await resp.text())
                pages = json.loads(text)['data']
                if len(pages) == 0:
                    self.start += 0
                    self.genres += 1
                    raise RuntimeWarning("开始获取{}分类".format(self.get_params()["tags"]))
                else:
                    self.start += 20
                    return pages

    async def get_subject(self, jsons):
        for x_json in range(len(jsons)):
            json = jsons[x_json]
            url = str(json['url'])
            id = str(json['id'])
            # 可能会要更新数据，还是不要跳过任何一个数据了
            # if Movie.query_by_id(id, self.session) is not None:
            #     continue
            movie = Movie(id=int(id))
            async with ClientSession(cookies=self.cookie, headers=self.header) as session:
                async with session.get(self.api_url + id, params=self.get_params(),
                                       proxy="http://" + str(self.proxy[0]) + ":" + str(self.proxy[1]),
                                       timeout=10) as resp:
                    subject_json = await resp.json()
                    assert resp.status == 200, "失败，理由如下{}".format(str(await resp.text()))
                    movie.name = subject_json['title']
                    movie.original_name = subject_json['original_title']
                    movie.poster = subject_json['images']['large']
                    movie.released = int(subject_json['year'])
                    movie.country = str(subject_json['countries'])
                    movie.douban_rating = subject_json['rating']['average']
                    movie.douban_votes = subject_json['ratings_count']
                    movie.polt = subject_json['summary']
                    movie.save(self.session)
                    if 'casts' in subject_json:
                        for man in subject_json['casts']:
                            filmman = Filmman(id=man['id'], name=man['name'])
                            filmman.save(self.session)
                            movie.append_filmman(filmman, Filmman.Role_Actor, self.session)
                    if 'directors' in subject_json:
                        for man in subject_json['directors']:
                            filmman = Filmman(id=man['id'], name=man['name'])
                            filmman.save(self.session)
                            movie.append_filmman(filmman, Filmman.Role_Director, self.session)
                    if 'writers' in subject_json:
                        for man in subject_json['writers']:
                            filmman = Filmman(id=man['id'], name=man['name'])
                            filmman.save(self.session)
                            movie.append_filmman(filmman, Filmman.Role_Writer, self.session)
                    good_proxy(self.proxy)
                    print("得到了{}的基本数据".format(movie.name))
            # 得到标签数据
            async with ClientSession(cookies=self.cookie, headers=self.header) as session:
                async with session.get(url, params=self.get_params(),
                                       proxy="http://" + str(self.proxy[0]) + ":" + str(self.proxy[1]),
                                       timeout=10) as resp:
                    html = await resp.text()
                    assert resp.status == 200, "失败，理由如下{}".format(str(await resp.text()))
                    html = etree.HTML(html)
                    tags = html.xpath('//*[@id="content"]/div[2]/div[2]/div[3]/div/a/text()')
                    if len(tags) == 0:
                        raise RuntimeWarning("得到了{}的标签数据获取失败".format(movie.name))
                    for x_tag in tags:
                        tag = Tag(name=x_tag)
                        tag = tag.save(self.session)
                        movie.append_tag(tag, self.session)
                    self.save_progress(x_json + 1)
                    good_proxy(self.proxy)
                    asyncio.sleep(1000)

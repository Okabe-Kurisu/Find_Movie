import json

from aiohttp import ClientSession, ClientOSError
from lxml import etree
from spider import spider_config as config
from sql.dbHelper import Movie, Filmman, Tag
from util.proxy import get_proxy, del_proxy


# 得到豆瓣搜索页面的json列表，返回
# {"directors": ["摩砂雪", "庵野秀明", "鹤卷和哉", "前田真宏"], "rate": "8.3", "cover_x": 2932,
#  "star": "40", "title": "福音战士新剧场版：Q","url": "https:\/\/movie.douban.com\/subject\/2567647\/",
#  "casts": ["林原惠美", "绪方惠美", "宫村优子", "石田彰", "三石琴乃"],
#  "cover": "https://img3.doubanio.com\/view\/photo\/s_ratio_poster\/public\/p1768906265.webp",
#  "id": "2567647","cover_y": 4025}


class Douban(object):
    base_url = 'https://movie.douban.com/'
    list_url = base_url + 'j/new_search_subjects'
    api_url = 'https://api.douban.com/v2/movie/subject/'

    # 初始化时自动得到header和cookie
    def __init__(self, session, proxy="", tag="", start=0, range="0,10", sort='S', genres='剧情'):
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
            'genres': self.genres,
        }
        return params

    def get_proxy(self):
        return "http://" + str(self.proxy[0]) + ':' + str(self.proxy[1])

    # 初始化cookie
    def init(self):
        self.cookie = config.get_cookie()
        self.header = config.get_header()
        del_proxy(self.proxy)
        self.proxy = get_proxy()

    # 得到搜索列表页面的url
    async def get_tpye_list(self):
        async with ClientSession(cookies=self.cookie, headers=self.header) as session:
            async with session.get(self.list_url, params=self.get_params(),
                                   proxy="http://" + str(self.proxy[0]) + ":" + str(self.proxy[1]),
                                   timeout=10) as resp:
                pages = json.loads(await resp.text())['data']
                if len(pages) == 0:
                    raise RuntimeWarning("该分类已经全部获取完毕")
                else:
                    self.start += 20
                    return pages

    async def get_subject(self, jsons):
        for json in jsons:
            url = str(json['url'])
            id = url.split("/")[-1]
            # 可能会要更新数据，还是不要跳过任何一个数据了
            # if Movie.query_by_id(id, self.session) is not None:
            #     continue
            movie = Movie(id=id)
            async with ClientSession(cookies=self.cookie, headers=self.header) as session:
                async with session.get(self.api_url + id, params=self.get_params(),
                                       proxy="http://" + str(self.proxy[0]) + ":" + str(self.proxy[1]),
                                       timeout=10) as resp:
                    html = await resp.text()
                    subject_json = json.loads(html)
                    movie.name = subject_json['title']
                    movie.original_name = subject_json['original_title']
                    movie.poster = subject_json['images']['large']
                    movie.released = int(subject_json['year'])
                    movie.country = subject_json['countries']
                    movie.douban_rating = subject_json['rating']['average']
                    movie.douban_votes = subject_json['ratings_count']
                    movie.polt = subject_json['summary']
                    movie.save(session)
                    if 'casts' in subject_json:
                        for man in subject_json['casts']:
                            filmman = Filmman(id=man['id'], name=man['name'])
                            filmman.save(session)
                            movie.append_filmman(filmman, Filmman.Role_Actor, session)
                    if 'directors' in subject_json:
                        for man in subject_json['directors']:
                            filmman = Filmman(id=man['id'], name=man['name'])
                            filmman.save(session)
                            movie.append_filmman(filmman, Filmman.Role_Director, session)
                    if 'writers' in subject_json:
                        for man in subject_json['writers']:
                            filmman = Filmman(id=man['id'], name=man['name'])
                            filmman.save(session)
                            movie.append_filmman(filmman, Filmman.Role_Writer, session)
            # 得到标签数据
            async with ClientSession(cookies=self.cookie, headers=self.header) as session:
                async with session.get(url, params=self.get_params(),
                                       proxy="http://" + str(self.proxy[0]) + ":" + str(self.proxy[1]),
                                       timeout=10) as resp:
                    html = await resp.text()
                    html = etree.parse(html)
                    tags = html.xpath('//*[@id="content"]/div[3]/div[2]/div[5]/div/a/text()')
                    for x in tags:
                        tag = Tag(name=x)
                        tag.save(session)
                        movie.append_tag(tag, session)

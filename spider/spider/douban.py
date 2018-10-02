# -*- coding: utf-8 -*-
# @Time    : 2018/10/1 11:40
# @Author  : Amadeus
# @Desc : 用来解析豆瓣的内容
import json
import spider.spider_config as config
from sql.dbHelper import DbHelper, Movie
from sql.redisHelper import RedisHelper
import spider.page as page


class TypeList:
    def __init__(self, tag="", range="0,10", sort='S'):
        # 豆瓣搜索页参数列表
        self.redis = RedisHelper()
        self.tag = tag
        self.range = range
        self.sort = sort
        self.genres = 0
        self.start = 0
        self.load_progress()

    def save_progress(self, len):
        self.start += len
        self.redis.set("start", self.start)
        self.redis.set("genres", self.genres)

    def load_progress(self):
        self.start = int(self.redis.get("start")) if self.redis.exists("start") else 0
        self.genres = int(self.redis.get("genres")) if self.redis.exists("genres") else 0

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

    async def get_tpye_list(self):
        text = await page.download('https://movie.douban.com/j/new_search_subjects', param=self.get_params())
        pages = json.loads(text)['data']
        if len(pages) == 0:
            self.start = 0
            self.genres += 1
            return "分类{}已经获取完成".format(self.get_params()['genres'])
        for page in pages:
            self.redis.set_add("pages", page)
        self.save_progress(len(pages))  # 存储进度
        return "得到了{}分类的第{}页, 共{}个数据".format(self.get_params()['genres'],
                                             int(self.get_params()['start'] / 20),
                                             len(pages))


class MovieParse:
    def __init__(self):
        self.redis = RedisHelper()
        self.session = DbHelper.get_session()

    async def get_movie(self):
        url = str(self.redis.set_randmember("pages"))[2:-1]
        self.redis.set_rem("page", url)
        id = url.split("/")[-2]
        movie = Movie(id=int(id))
        text = await page.download(url)
# -*- coding: utf-8 -*-
# @Time    : 2018/10/1 11:40
# @Author  : Amadeus
# @Desc : 用来解析豆瓣的内容
import json
import traceback

from lxml import etree

import spider.spider_config as config
from sql.dbHelper import Movie, Tag, Filmman
from sql.redisHelper import RedisHelper
import spider.page as page


class TypeList:
    def __init__(self, tag="", range="0,10", sort='S', redis=RedisHelper()):
        # 豆瓣搜索页参数列表
        self.redis = redis
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

    async def get_type_list(self):
        import spider.page as page
        text = await page.download('https://movie.douban.com/j/new_search_subjects', param=self.get_params())
        pages = json.loads(text)['data']
        if len(pages) == 0:
            self.start = 0
            self.genres += 1
            self.save_progress(len(pages))  # 存储进度
            return "分类{}已经获取完成".format(self.get_params()['genres'])
        self.save_progress(len(pages))  # 存储进度
        for page in pages:
            self.redis.set_add("pages", page['url'])
        return "得到了{}分类的第{}页, 共{}个数据".format(self.get_params()['genres'],
                                             int(self.get_params()['start'] / 20),
                                             len(pages))


class MovieParse:
    def __init__(self, redis=RedisHelper()):
        self.redis = redis
        self.url = str(self.redis.set_randmember("pages"))[2:-1]
        self.movie = None
        self.redis.set_rem("pages", self.url)

    async def get_movie(self):
        id = self.url.split("/")[-2]
        self.movie = Movie(id=int(id))
        if self.movie.query():
            return "电影《{}》已经存在".format(self.movie.query().name)
        html = await page.download('https://api.douban.com/v2/movie/subject/' + id)
        if not html:
            return "电影《{}》下载失败".format(self.movie.name)
        if self.movie.query():
            return "电影《{}》已经存在".format(self.movie.name)
        try:
            subject_json = json.loads(html)
            self.movie.name = subject_json['title']
            self.movie.original_name = subject_json['original_title']
            self.movie.poster = subject_json['images']['large']
            self.movie.released = int(''.join([x for x in '1997年' if x in "0123456789"])) if subject_json[
                'year'] else 0
            self.movie.country = str(subject_json['countries'])
            self.movie.douban_rating = subject_json['rating']['average']
            self.movie.douban_votes = subject_json['ratings_count']
            self.movie.polt = subject_json['summary']
            self.movie.save()

            await self.get_info()
            return "得到了《{}》的基本数据".format(self.movie.name)
        except Exception:
            self.redis.set_add("pages", self.url)
            traceback.print_exc()

    async def get_info(self):
        html = await page.download(self.url)
        html = etree.HTML(html)

        directors = html.xpath('//*[@rel="v:directedBy"]/text()')
        if directors:
            for man in directors:
                for x in man.split(" / "):
                    filmman = Filmman(name=x)
                    self.movie.append_filmman(filmman, Filmman.ROLE_DIRECTOR)

        actors = html.xpath('//*[@rel="v:starring"]/text()')
        if actors:
            for man in directors:
                for x in man.split(" / "):
                    filmman = Filmman(name=x)
                    self.movie.append_filmman(filmman, Filmman.ROLE_ACTOR)

        tags = html.xpath('//*[@class="tags-body"]/a/text()')
        if tags:
            for x_tag in tags:
                tag = Tag(name=x_tag)
                self.movie.append_tag(tag)

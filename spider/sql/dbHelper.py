# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker, relationship, mapper
import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table
from sqlalchemy import Column, String, Integer, Text, Float, ForeignKey
import traceback

Base = declarative_base()


class DbHelper:
    def __init__(self):
        conn_url = 'mysql+pymysql://' + config.mysql_username + ':' + config.mysql_passwd + '@' + config.mysql_host + '/' + \
                   config.mysql_dbname
        self.engine = create_engine(conn_url, pool_size=100, echo=False, pool_recycle=5 * 60)
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()

    def init_DB(self):
        Base.metadata.create_all(self.engine)

    def drop_DB(self):
        Base.metadata.drop_all(self.engine)

    @staticmethod
    def get_session():
        conn_url = 'mysql+pymysql://' + config.mysql_username + ':' + config.mysql_passwd + '@' + config.mysql_host + '/' + \
                   config.mysql_dbname
        engine = create_engine(conn_url, pool_size=100, echo=False)
        db_session = sessionmaker(bind=engine)
        return db_session()


class Movie(Base):  # 电影表，记录电影的各种信息
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 豆瓣id就是唯一id
    imdb_id = Column(String(10))
    name = Column(String(120), nullable=True)
    original_name = Column(String(120))  # 非中文名
    poster = Column(String(150), default='no pic')  # 海报地址
    released = Column(String(10))  # 发行年份
    country = Column(String(200))  # 制片国家
    runtime = Column(String(5))  # 电影时长 omdb获得
    language = Column(String(70))  # 发行语言 omdb获得
    douban_rating = Column(Float)
    douban_votes = Column(Integer)  # 豆瓣评分人数
    imdb_rating = Column(Float)  # omdb获得
    imdb_votes = Column(Integer)  # imdb评分人数
    polt = Column(Text)  # 剧情介绍
    filmmans = relationship('Filmman'
                            , secondary='filmman_movie'
                            , backref='movies')
    tags = relationship('Tag'
                        , secondary='tag_movie'
                        , backref='movies')
    session = DbHelper.get_session()

    def save(self):
        temp = self.query()
        if not temp:
            self.session.merge(self)
            return self
        return temp

    def query(self):  # 检查是否重复保存了数据
        query = self.session.query(Movie)
        if self.id:
            query = query.filter(Movie.id == id)
        return query.first()

    def query_all_filmmaker(self):
        filmmans = self.session.query(Movie).filter(Movie.id == self.id).first().filmmans
        return filmmans

    def query_all_tag(self):
        tags = self.session.query(Movie).filter(Movie.id == self.id).first().tags
        return tags

    def append_filmman(self, filmman, role):
        fm = Filmman_movie(fid=filmman.id, mid=self.id, role=role)
        filmman.session.close()
        fm.save()

    def append_tag(self, tag):
        temp = tag.query()
        if temp:
            tag = temp
        tags = self.query_all_tag()
        for t in tags:
            if t.id == tag.id:
                return
        tm = Tag_movie(tid=tag.id, mid=self.id)
        tm.save()


# 影人与电影关系
class Filmman_movie(Base):
    __tablename__ = 'filmman_movie'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fid = Column(Integer, ForeignKey('filmman.id'))
    mid = Column(Integer, ForeignKey('movie.id'))
    role = Column(Integer, default=0)
    session = DbHelper.get_session()

    def save(self):
        self.session.merge(self)
        self.session.close()

    def query_by_fidmid(self):
        fm = self.session.query(Filmman_movie) \
            .filter(Filmman_movie.mid == self.mid and Filmman_movie.fid == self.fid).first()
        return fm


# 影人表，记录导演演员编剧的信息
class Filmman(Base):
    __tablename__ = 'filmman'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    name_en = Column(String(150))
    aka = Column(String(20))
    aka_en = Column(String(50))
    born_date = Column(String(10))
    born_place = Column(String(20))
    job = Column(String(20))
    avatar = Column(String(100))
    session = DbHelper.get_session()

    ROLE_DIRECTOR = 1
    ROLE_ACTOR = 10
    ROLE_WRITER = 100

    def save(self):
        temp = self.query()
        if temp:
            return temp
        self.session.merge(self)
        self.session.close()
        return self

    def query(self):
        query = self.session.query(Filmman)
        if self.id:
            query = query.filter(Filmman.id == self.id)
        if self.name:
            query = query.filter(Filmman.name == self.name)
        return query.first()

    def query_all_movie(self):
        filmmaker = self.session.query(Filmman).filter(Filmman.id == self.id).first()
        movies = filmmaker.movies
        return movies


# 电影和标签的关系
class Tag_movie(Base):
    __tablename__ = 'tag_movie'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tid = Column(Integer, ForeignKey('tag.id'))
    mid = Column(Integer, ForeignKey('movie.id'))
    session = DbHelper.get_session()

    def save(self):
        self.session.merge(self)
        self.session.close()

    def query_by_tidmid(self):
        tm = self.session.query(Filmman_movie) \
            .filter(Tag_movie.tid == self.tid and Tag_movie.mid == self.mid).first()
        return tm


# 电影标签
class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True, unique=True)
    session = DbHelper.get_session()

    def save(self):
        temp = self.query()
        if temp:
            return temp
        self.session.merge(self)
        self.session.close()
        return self

    def query(self):
        query = self.session.query(Tag)
        if self.id:
            query = query.filter(Tag.id == self.id)
        if self.name:
            query = query.filter(Tag.name == self.name)
        return query.first()

    def query_all_movie(self):
        tag = self.session.query(Tag).filter(Tag.id == self.id).first()
        movies = tag.movies
        return movies


if __name__ == "__main__":
    s = DbHelper()
    s.init_DB()

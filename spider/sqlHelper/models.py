# -*- coding: utf-8 -*-
# @Time    : 2018/10/7 18:56
# @Author  : Amadeus
# @Desc :
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, VARCHAR, Integer, Text, Float, ForeignKey
from sqlalchemy.orm import relationship

from sqlHelper.db import db as db

Base = declarative_base()


class Movie(Base):  # 电影表，记录电影的各种信息
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 豆瓣id就是唯一id
    imdb_id = Column(VARCHAR(10))
    name = Column(VARCHAR(250), nullable=True)
    original_name = Column(VARCHAR(250))  # 非中文名
    poster = Column(VARCHAR(150), default='no pic')  # 海报地址
    released = Column(Integer, default=0)  # 发行年份
    country = Column(VARCHAR(200))  # 制片国家
    runtime = Column(VARCHAR(5))  # 电影时长 omdb获得
    language = Column(VARCHAR(70))  # 发行语言 omdb获得
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
    session = db.session

    def save(self):
        if self.id:
            self.session.merge(self)
            return self
        temp = self.query()
        if not temp:
            self.session.add(self)
        return self.query()

    def query(self):  # 检查是否重复保存了数据
        query = self.session.query(Movie)
        if self.id:
            query = query.filter(Movie.id == self.id)
        return query.all()

    def query_all_filmmaker(self):
        filmmans = self.session.query(Movie).filter(Movie.id == self.id).first().filmmans
        return filmmans

    def query_all_tag(self):
        tags = self.session.query(Movie).filter(Movie.id == self.id).first().tags
        return tags

    def append_filmman(self, filmman, role):
        filmman = filmman.save()
        fm = Filmman_movie(fid=filmman.id, mid=self.id, role=role)
        if not fm.query_by_fidmid():
            fm.save()

    def append_tag(self, tag):
        tag = tag.save()
        tm = Tag_movie(tid=tag.id, mid=self.id)
        if not tm.query_by_tidmid():
            tm.save()


# 影人与电影关系
class Filmman_movie(Base):
    __tablename__ = 'filmman_movie'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fid = Column(Integer, ForeignKey('filmman.id'))
    mid = Column(Integer, ForeignKey('movie.id'))
    role = Column(Integer, default=0)
    session = db.session

    def save(self):
        self.session.add(self)
        return self

    def query_by_fidmid(self):
        fm = self.session.query(Filmman_movie) \
            .filter(Filmman_movie.mid == self.mid and Filmman_movie.fid == self.fid).first()
        return fm


# 影人表，记录导演演员编剧的信息
class Filmman(Base):
    __tablename__ = 'filmman'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(150), nullable=True)
    name_en = Column(VARCHAR(150))
    aka = Column(VARCHAR(20))
    aka_en = Column(VARCHAR(50))
    born_date = Column(VARCHAR(10))
    born_place = Column(VARCHAR(20))
    job = Column(VARCHAR(20))
    avatar = Column(VARCHAR(100))
    session = db.session

    ROLE_DIRECTOR = 1
    ROLE_ACTOR = 10
    ROLE_WRITER = 100

    def save(self):
        if self.id:
            self.session.merge(self)
            return self
        temp = self.query()
        if not temp:
            self.session.add(self)
        return self.query()

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
    session = db.session

    def save(self):
        self.session.add(self)
        return self

    def query_by_tidmid(self):
        tm = self.session.query(Filmman_movie) \
            .filter(Tag_movie.tid == self.tid and Tag_movie.mid == self.mid).first()
        return tm


# 电影标签
class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50), nullable=True, unique=True)
    session = db.session

    def save(self):
        if self.id:
            self.session.merge(self)
            return self
        temp = self.query()
        if not temp:
            self.session.add(self)
        return self.query()

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

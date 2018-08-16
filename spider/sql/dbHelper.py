# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker, relationship, mapper
import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table
from sqlalchemy import Column, String, Integer, Text, Float, ForeignKey
import traceback

conn_url = 'mysql+pymysql://' + config.mysql_username + ':' + config.mysql_passwd + '@' + config.mysql_host + '/' + \
           config.mysql_dbname
engine = create_engine(conn_url, pool_size=100)
DBSession = sessionmaker(bind=engine, autocommit=False)
Base = declarative_base()


class Movie(Base):  # 电影表，记录电影的各种信息
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 豆瓣id就是唯一id
    imdb_id = Column(String(10))
    name = Column(String(120), nullable=True)  # 57据说是世界上最长的电影名长度
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

    def save(self, session):
        temp = Movie.query_by_id(self.id, session)
        if temp is None:
            session.merge(self)
            return self
        return temp

    @staticmethod
    def query_by_id(id, session):  # 检查是否重复保存了数据
        movie = session.query(Movie).filter(Movie.id == id).first()
        return movie

    def query_all_filmmaker(self, session):
        filmmans = session.query(Movie).filter(Movie.id == self.id).first().filmmans
        return filmmans

    def query_all_tag(self, session):
        tags = session.query(Movie).filter(Movie.id == self.id).first().tags
        return tags

    def append_filmman(self, filmman, role, session):
        fm = Filmman_movie(fid=filmman.id, mid=self.id, role=role)
        fm.save(session)

    def append_tag(self, tag, session):
        temp = Tag.query_by_name(tag.name, session)
        if temp is not None:
            tag = temp
        tags = self.query_all_tag(session)
        for t in tags:
            if t.id == tag.id:
                return
        tm = Tag_movie(tid=tag.id, mid=self.id)
        tm.save(session)


# 影人与电影关系
class Filmman_movie(Base):
    __tablename__ = 'filmman_movie'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fid = Column(Integer, ForeignKey('filmman.id'))
    mid = Column(Integer, ForeignKey('movie.id'))
    role = Column(Integer, default=0)

    def save(self, session):
        session.merge(self)

    def query_by_fidmid(self, session):
        fm = session.query(Filmman_movie) \
            .filter(Filmman_movie.mid == self.mid and Filmman_movie.fid == self.fid).first()
        return fm


class Filmman(Base):  # 影人表，记录导演演员编剧的信息
    __tablename__ = 'filmman'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(), nullable=True)
    name_en = Column(String(150))
    aka = Column(String(20))
    aka_en = Column(String(50))
    born_date = Column(String(10))
    born_place = Column(String(20))
    job = Column(String(20))
    avatar = Column(String(100))

    Role_Director = 1
    Role_Actor = 10
    Role_Writer = 100

    def save(self, session):
        session.merge(self)

    @staticmethod
    def query_by_id(id, session):
        filmmaker = session.query(Filmman).filter(Filmman.id == id).first()
        return filmmaker

    @staticmethod
    def query_by_id(id, session):
        filmmaker = session.query(Filmman).filter(Filmman.id == id).first()
        return filmmaker

    @staticmethod
    def query_by_name(name, session):
        filmmaker = session.query(Filmman).filter(Filmman.name == name).first()
        return filmmaker

    def query_all_movie(self, session):
        filmmaker = session.query(Filmman).filter(Filmman.id == self.id).first()
        movies = filmmaker.movies
        return movies


# 电影和标签的关系
# 影人与电影关系
class Tag_movie(Base):
    __tablename__ = 'tag_movie'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tid = Column(Integer, ForeignKey('tag.id'))
    mid = Column(Integer, ForeignKey('movie.id'))

    def save(self, session):
        session.merge(self)

    def query_by_tidmid(self, session):
        tm = session.query(Filmman_movie) \
            .filter(Tag_movie.tid == self.tid and Tag_movie.mid == self.mid).first()
        return tm


class Tag(Base):  # 电影标签
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True, unique=True)

    def row2dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d

    def save(self, session):
        session.merge(self)

    @staticmethod
    def query_by_id(id, session):
        tag = session.query(Tag).filter(Tag.id == id).first()
        return tag

    @staticmethod
    def query_by_name(name, session):
        tag = session.query(Tag).filter(Tag.name == name).first()
        return tag

    def query_all_movie(self, session):
        tag = session.query(Tag).filter(Tag.id == self.id).first()
        movies = tag.movies
        return movies

    @staticmethod
    def get_tag(name, session):
        temp = Tag.query_by_name(name, session)
        if temp is None:
            tag = Tag(name=name)
            tag.save(session)
            return tag
        return temp


# 进度表
class Progress(Base):
    __tablename__ = 'progress'
    id = Column(Integer, primary_key=True)
    start = Column(Integer)
    genres = Column(Integer)

    def save(self, session):
        session.merge(self)

    @staticmethod
    def load(session):
        progress = session.query(Progress).filter(Progress.id == 1).first()
        return progress


def init_DB():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        traceback.print_exc()


def drop_DB():
    try:
        Base.metadata.drop_all(engine)
    except Exception as e:
        traceback.print_exc()


if __name__ == "__main__":
    session = DBSession()
    movie = Movie(id="1213321")
    print(movie.query_by_id(1213321, session))

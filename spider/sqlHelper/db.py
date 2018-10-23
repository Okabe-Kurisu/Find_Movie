# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config
from sqlalchemy import create_engine


class db:
    base = declarative_base()
    conn_url = 'mysql+pymysql://' + config.mysql_username + ':' + config.mysql_passwd + '@' + config.mysql_host + '/' + \
               config.mysql_dbname
    engine = create_engine(conn_url, pool_size=100, echo=False, pool_recycle=5 * 60)
    db_session = sessionmaker(bind=engine)
    session = db_session()

    def init_DB(self):
        self.base.metadata.create_all(self.engine)

    def drop_DB(self):
        self.base.metadata.drop_all(self.engine)

    def get_session(self):
        return self.session


if __name__ == "__main__":
    d = db()
    d.init_DB()

import time

from redis import StrictRedis, ConnectionPool


class RedisHelper:
    def __init__(self):
        pool = ConnectionPool.from_url('//@localhost:6379/')
        redis = StrictRedis(connection_pool=pool)
        self.redis = redis

    def set(self, key, value):
        return self.redis.setnx(key, value)

    def mset(self, dict):
        return self.redis.mset(map)

    def get(self, key):
        return self.redis.get(key)

    def delete(self, key):
        return self.redis.delete(key)

    def randomkey(self):
        return self.redis.randomkey()

    def dbsize(self):
        return self.redis.dbsize()

    def getall(self):
        return self.redis.keys()


if __name__ == "__main__":
    redis = RedisHelper()
    storage = 0
    print("当前还有{}条数据等待存储".format(redis.dbsize()))
    while True:
        size = redis.dbsize()
        if storage != size:
            storage = size
            print("当前还有{}条数据等待存储".format(size)) #, redis.getall()))
        time.sleep(1)
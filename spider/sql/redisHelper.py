import time

from redis import StrictRedis, ConnectionPool


class RedisHelper:
    def __init__(self):
        pool = ConnectionPool.from_url('//@localhost:6379/')
        redis = StrictRedis(connection_pool=pool)
        self.redis = redis

    def flush(self):
        return self.redis.flushall()

    def set(self, key, value):
        return self.redis.set(key, value)

    def exists(self, key):
        return self.redis.exists(key)

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

    def lpush(self, key, value):
        return self.redis.lpush(key, value)

    def lpop(self, key):
        return self.redis.lpop(key)

    def lget(self, key):
        return self.redis.lrange(key, 0, 0)

    def getall(self):
        return self.redis.keys()

    def set_add(self, key, value):
        return self.redis.sadd(key, value)

    def set_randmember(self, key):
        return self.redis.srandmember(key)

    def set_rem(self, key, value):
        return self.redis.srem(key, value)

    def set_size(self, key):
        return self.redis.scard(key)


if __name__ == "__main__":
    redis = RedisHelper()
    print(redis.set_size("pages"))
    # storage = 0
    # print("当前还有{}条数据等待存储".format(redis.dbsize()))
    # while True:
    #     size = redis.dbsize()
    #     if storage != size:
    #         storage = size
    #         print("当前还有{}条数据等待存储".format(size)) #, redis.getall()))
    #     time.sleep(1)
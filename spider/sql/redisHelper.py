from redis import StrictRedis, ConnectionPool


class RedisHelper:
    def __init__(self):
        pool = ConnectionPool.from_url('//@localhost:6379/')
        redis = StrictRedis(connection_pool=pool)
        self.redis = redis

    def set(self, key, value):
        return self.redis.setnx(key, value)

    def msetnx(self, map):
        return self.redis.setnx(map)

    def get(self, key):
        return self.redis.get(key)

    def delete(self, key):
        return self.redis.delete(key)

    def randomkey(self):
        return self.redis.randomkey()


if __name__ == "__main__":
    redis = RedisHelper()
    print(redis.set("1", {"asd":1}))
    print(redis.get("1"))
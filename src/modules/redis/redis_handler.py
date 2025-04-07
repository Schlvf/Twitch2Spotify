from typing import TypeVar

from redis import Redis

from core import EnvWrapper, time_diff

T = TypeVar("T")


class RedisHandler:
    def __new__(cls):
        """Singleton handler"""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
            cls.redis_client = Redis(
                host=EnvWrapper().REDIS_HOST,
                port=6379,
                decode_responses=True,
            )
        return cls.instance

    @time_diff
    def ping(self):
        res = self.redis_client.ping()
        return res

    @time_diff
    def set_pair(self, name: str, value, expiration: int | None = None):
        res = self.redis_client.set(name=name, value=value, ex=expiration)
        return res

    @time_diff
    def get_pair(self, name: str):
        res = self.redis_client.get(name=name)
        return res

    @time_diff
    def set_dict(self, name: str, payload: dict):
        res = self.redis_client.hset(name=name, mapping=payload)
        return res

    @time_diff
    def get_dict(self, name: str, class_type: T | None = None) -> T:
        res = self.redis_client.hgetall(name=name)
        if class_type and res:
            return class_type(**res)
        return res

    @time_diff
    def delete_dict(self, name: str, key: str):
        res = self.redis_client.hdel(name=name, keys=key)
        return res

    @time_diff
    def exists_dict(self, name: str, key: str):
        res = self.redis_client.hexists(name=name, key=key)
        return res

    @time_diff
    def set_expire(self, name: str, seconds: int):
        res = self.redis_client.expire(name=name, time=seconds)
        return res

    @time_diff
    def flush_all(self):
        res = self.redis_client.flushall()
        return res

    @time_diff
    def count(self):
        res = self.redis_client.dbsize()
        return res

    @time_diff
    def get_keys(self, pattern: str, count: int):
        res = self.redis_client.scan_iter(match=pattern, count=count)
        return list(res)

    @time_diff
    def delete_keys(self, pattern: str, count: int):
        res = list(self.redis_client.scan_iter(match=pattern, count=count))
        for key in res:
            self.redis_client.delete(key)
        return len(res)

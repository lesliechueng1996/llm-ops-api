"""
@Time   : 2024/12/20 19:49
@Author : Leslie
@File   : redis_lock.py
"""

from redis import Redis


def acquire_lock(
    redis_client: Redis, key: str, value: str, expire_time: int = 60
) -> bool:
    """
    获取分布式锁
    :param redis_client: redis客户端
    :param key: 锁的key
    :param value: 锁的value
    :param expire_time: 锁的过期时间(秒)
    :return: 是否获取成功
    """
    result = redis_client.set(key, value, nx=True, ex=expire_time)
    return result is True


def release_lock(redis_client: Redis, key: str, value: str):
    lua_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
    """
    result = redis_client.eval(lua_script, 1, key, value)
    return result == 1

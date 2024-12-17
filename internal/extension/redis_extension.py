"""
@Time   : 2024/12/17 20:47
@Author : Leslie
@File   : redis_extension.py
"""

from flask import Flask
import redis
from redis.connection import Connection, SSLConnection

redis_client = redis.Redis()


def init_app(app: Flask):
    connection_class = Connection
    if app.config.get("REDIS_USE_SSL", False):
        connection_class = SSLConnection

    redis_client.connection_pool = redis.ConnectionPool(
        host=app.config.get("REDIS_HOST", "localhost"),
        port=app.config.get("REDIS_PORT", 6379),
        db=app.config.get("REDIS_DB", 0),
        username=app.config.get("REDIS_USERNAME", None),
        password=app.config.get("REDIS_PASSWORD", None),
        connection_class=connection_class,
        encoding="utf-8",
        encoding_errors="strict",
        decode_responses=False,
    )

    app.extensions["redis"] = redis_client

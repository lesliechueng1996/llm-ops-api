"""
@Time   : 2024/12/2 00:06
@Author : Leslie
@File   : default_config.py
"""

DEFAULT_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": "",
    "SQLALCHEMY_ECHO": "True",
    "SQLALCHEMY_POOL_RECYCLE": "3600",
    "SQLALCHEMY_POOL_SIZE": "30",
    "WTF_CSRF_ENABLED": "False",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_DB": "0",
    "REDIS_USERNAME": "",
    "REDIS_PASSWORD": "",
    "REDIS_USE_SSL": "False",
    "CELERY_BROKER_DB": "1",
    "CELERY_RESULT_BACKEND_DB": "1",
    "CELERY_TASK_IGNORE_RESULT": "False",
    "CELERY_RESULT_EXPIRES": "3600",
    "CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP": "True",
}

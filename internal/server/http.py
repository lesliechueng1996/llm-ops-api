"""
@Time   : 2024/12/1 05:41
@Author : Leslie
@File   : http.py
"""
from flask import Flask

from internal.router import Router
from config import Config

class Http(Flask):
    def __init__(self, *args, router: Router, config: Config, **kwargs):
        super().__init__(*args, **kwargs)
        router.register_router(self)
        self.config.from_object(config)
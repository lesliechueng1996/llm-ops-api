"""
@Time   : 2024/12/1 05:41
@Author : Leslie
@File   : http.py
"""
from flask import Flask

from internal.router import Router

class Http(Flask):
    def __init__(self, *args, router: Router, **kwargs):
        super().__init__(*args, **kwargs)
        router.register_router(self)
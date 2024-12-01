"""
@Time   : 2024/12/1 05:30
@Author : Leslie
@File   : router.py
"""
from dataclasses import dataclass
from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler

@inject
@dataclass
class Router:
    """路由"""
    app_handler: AppHandler

    def register_router(self, app: Flask):
        """注册路由"""
        bp = Blueprint("llmops", __name__, url_prefix="")
        bp.add_url_rule("/ping", view_func=self.app_handler.ping)

        app.register_blueprint(bp)

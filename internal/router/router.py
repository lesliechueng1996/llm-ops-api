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
        bp.add_url_rule(
            "/app/completion", methods=["POST"], view_func=self.app_handler.completion
        )

        bp.add_url_rule("/app", methods=["POST"], view_func=self.app_handler.create_app)
        bp.add_url_rule("/app/<uuid:id>", view_func=self.app_handler.get_app)
        bp.add_url_rule(
            "/app/<uuid:id>", methods=["PUT"], view_func=self.app_handler.update_app
        )
        bp.add_url_rule(
            "/app/<uuid:id>", methods=["DELETE"], view_func=self.app_handler.delete_app
        )

        app.register_blueprint(bp)

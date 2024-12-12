"""
@Time   : 2024/12/1 05:30
@Author : Leslie
@File   : router.py
"""

from dataclasses import dataclass
from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler, BuiltinToolHandler


@inject
@dataclass
class Router:
    """路由"""

    app_handler: AppHandler
    builtin_tool_handler: BuiltinToolHandler

    def register_router(self, app: Flask):
        """注册路由"""
        bp = Blueprint("llmops", __name__, url_prefix="")
        bp.add_url_rule("/ping", view_func=self.app_handler.ping)
        bp.add_url_rule(
            "/apps/<uuid:app_id>/debug",
            methods=["POST"],
            view_func=self.app_handler.debug,
        )

        # bp.add_url_rule("/app", methods=["POST"], view_func=self.app_handler.create_app)
        # bp.add_url_rule("/app/<uuid:id>", view_func=self.app_handler.get_app)
        # bp.add_url_rule(
        #     "/app/<uuid:id>", methods=["PUT"], view_func=self.app_handler.update_app
        # )
        # bp.add_url_rule(
        #     "/app/<uuid:id>", methods=["DELETE"], view_func=self.app_handler.delete_app
        # )

        # built-in tools
        bp.add_url_rule(
            "/builtin-tools/categories",
            view_func=self.builtin_tool_handler.get_builtin_tools_categories,
        )
        bp.add_url_rule(
            "/builtin-tools", view_func=self.builtin_tool_handler.get_builtin_tools
        )
        bp.add_url_rule(
            "/builtin-tools/<string:provider_name>/tools/<string:tool_name>",
            view_func=self.builtin_tool_handler.get_provider_tool,
        )

        app.register_blueprint(bp)

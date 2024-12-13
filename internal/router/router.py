"""
@Time   : 2024/12/1 05:30
@Author : Leslie
@File   : router.py
"""

from dataclasses import dataclass
from flask import Flask, Blueprint
from injector import inject

from internal.handler import AppHandler, BuiltinToolHandler, ApiToolHandler


@inject
@dataclass
class Router:
    """路由"""

    app_handler: AppHandler
    builtin_tool_handler: BuiltinToolHandler
    api_tool_handler: ApiToolHandler

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
        bp.add_url_rule(
            "/builtin-tools/<string:provider_name>/icon",
            view_func=self.builtin_tool_handler.get_provider_icon,
        )

        # api tools
        bp.add_url_rule(
            "/api-tools/validate-openapi-schema",
            methods=["POST"],
            view_func=self.api_tool_handler.validate_openapi_schema,
        )
        bp.add_url_rule(
            "/api-tools",
            methods=["POST"],
            view_func=self.api_tool_handler.create_api_tools,
        )

        app.register_blueprint(bp)

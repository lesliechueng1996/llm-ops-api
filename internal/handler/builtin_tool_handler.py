"""
@Time   : 2024/12/12 21:10
@Author : Leslie
@File   : builtin_tool_handler.py
"""

from io import BytesIO
from injector import inject
from dataclasses import dataclass
from internal.service import BuiltinToolService
from pkg.response import success_json
from flask import send_file


@inject
@dataclass
class BuiltinToolHandler:

    builtin_tool_service: BuiltinToolService

    def get_builtin_tools_categories(self):
        results = self.builtin_tool_service.get_builtin_tools_categories()
        return success_json(results)

    def get_builtin_tools(self):
        results = self.builtin_tool_service.get_builtin_tools()
        return success_json(results)

    def get_provider_tool(self, provider_name: str, tool_name: str):
        result = self.builtin_tool_service.get_provider_tool(provider_name, tool_name)
        return success_json(result)

    def get_provider_icon(self, provider_name: str):
        icon_bytes, mimetype = self.builtin_tool_service.get_provider_icon(
            provider_name
        )
        return send_file(BytesIO(icon_bytes), mimetype=mimetype)

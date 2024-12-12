"""
@Time   : 2024/12/12 21:10
@Author : Leslie
@File   : builtin_tool_handler.py
"""

from injector import inject
from dataclasses import dataclass
from internal.service import BuiltinToolService
from pkg.response import success_json


@inject
@dataclass
class BuiltinToolHandler:

    builtin_tool_service: BuiltinToolService

    def get_builtin_tools(self):
        results = self.builtin_tool_service.get_builtin_tools()
        return success_json(results)

    def get_provider_tool(self, provider_name: str, tool_name: str):
        result = self.builtin_tool_service.get_provider_tool(provider_name, tool_name)
        return success_json(result)

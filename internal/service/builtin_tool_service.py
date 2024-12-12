"""
@Time   : 2024/12/12 21:10
@Author : Leslie
@File   : builtin_tool_service.py
"""

from injector import inject
from dataclasses import dataclass

from pydantic import BaseModel

from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.core.tools.builtin_tools.categories import BuiltinCategoryManager
from internal.exception import NotFoundException


@inject
@dataclass
class BuiltinToolService:
    builtin_provider_manager: BuiltinProviderManager
    builtin_category_manager: BuiltinCategoryManager

    def get_builtin_tools_categories(self):
        categories = self.builtin_category_manager.category_map.values()
        return [
            {
                "category": category["entity"].category,
                "name": category["entity"].name,
                "icon": category["icon"],
            }
            for category in categories
        ]

    def get_builtin_tools(self) -> list:
        results = []
        providers = self.builtin_provider_manager.get_providers()
        for provider in providers:
            tools = []
            for tool_entity in provider.get_tool_entities():
                tool_func = provider.get_tool(tool_entity.name)
                inputs = self._get_input_from_tool(tool_func)
                tool = {**tool_entity.model_dump(), "inputs": inputs}
                tools.append(tool)

            result_provider = {
                **provider.provider_entity.model_dump(exclude=["icon"]),
                "tools": tools,
            }
            results.append(result_provider)
        return results

    def get_provider_tool(self, provider_name: str, tool_name: str):
        provider = self.builtin_provider_manager.get_provider(provider_name)
        if provider is None:
            raise NotFoundException(f"该提供商{provider_name}不存在")
        tool = provider.get_tool(tool_name)
        tool_entity = provider.get_tool_entity(tool_name)
        if tool is None or tool_entity is None:
            raise NotFoundException(f"该工具{tool_name}不存在")

        provider_entity = provider.provider_entity
        inputs = self._get_input_from_tool(tool)
        return {
            "provider": {
                **provider_entity.model_dump(exclude=["icon", "created_at"]),
            },
            **tool_entity.model_dump(),
            "created_at": provider_entity.created_at,
            "inputs": inputs,
        }

    @classmethod
    def _get_input_from_tool(cls, tool_func) -> dict:
        inputs = []
        if hasattr(tool_func, "args_schema") and issubclass(
            tool_func.args_schema, BaseModel
        ):
            for (
                field_name,
                model_field,
            ) in tool_func.args_schema.model_fields.items():
                inputs.append(
                    {
                        "name": field_name,
                        "description": model_field.description or "",
                        "required": model_field.is_required(),
                        "type": model_field.annotation.__name__,
                    }
                )
        return inputs

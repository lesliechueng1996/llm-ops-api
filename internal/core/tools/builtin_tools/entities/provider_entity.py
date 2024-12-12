"""
@Time   : 2024/12/12 15:32
@Author : Leslie
@File   : provider_entity.py
"""

from pydantic import BaseModel, Field
from .tool_entity import ToolEntity
from langchain_core.tools import BaseTool
from os import path
import yaml
from internal.lib import dynamic_import
from typing import Callable


class ProviderEntity(BaseModel):
    name: str
    label: str
    description: str
    icon: str
    background: str
    category: str


class Provider(BaseModel):
    name: str
    position: int
    provider_entity: ProviderEntity
    tool_entity_map: dict[str, ToolEntity] = Field(default_factory=dict)
    tool_func_map: dict[str, BaseTool] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_provider_tools()

    def get_tool(self, tool_name: str) -> Callable[..., BaseTool]:
        return self.tool_func_map.get(tool_name)

    def get_tool_entity(self, tool_name: str) -> ToolEntity:
        return self.tool_entity_map.get(tool_name)

    def get_tool_entities(self) -> list[ToolEntity]:
        return list(self.tool_entity_map.values())

    def _init_provider_tools(self):
        current_dir = path.dirname(path.abspath(__file__))
        providers_dir = path.join(path.dirname(current_dir), "providers")
        tools_dir = path.join(providers_dir, self.name)
        positions_file_path = path.join(tools_dir, "positions.yaml")
        with open(positions_file_path, encoding="utf-8") as f:
            positions_data: list[str] = yaml.safe_load(f)

        for tool_name in positions_data:
            # 加载工具函数
            tool_func = dynamic_import(
                f"internal.core.tools.builtin_tools.providers.{self.name}", tool_name
            )
            self.tool_func_map[tool_name] = tool_func

            # 加载工具实体
            tool_file = path.join(tools_dir, f"{tool_name}.yaml")
            with open(tool_file, encoding="utf-8") as f:
                tool_data = yaml.safe_load(f)
            tool_entity = ToolEntity(**tool_data)
            self.tool_entity_map[tool_name] = tool_entity
        pass

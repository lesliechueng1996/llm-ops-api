"""
@Time   : 2024/12/12 15:32
@Author : Leslie
@File   : builtin_provider_manager.py
"""

from pydantic import Field, BaseModel
from internal.core.tools.builtin_tools.entities import Provider, ProviderEntity
from injector import singleton, inject
from os import path
import yaml
from langchain_core.tools import BaseTool
from typing import Callable


@inject
@singleton
class BuiltinProviderManager(BaseModel):
    provider_map: dict[str, Provider] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_provider_map()

    def get_provider(self, provider_name: str) -> Provider:
        return self.provider_map.get(provider_name)

    def get_providers(self) -> list[Provider]:
        return list(self.provider_map.values())

    def get_all_provider_entities(self) -> list[ProviderEntity]:
        return [provider.provider_entity for provider in self.provider_map.values()]

    def get_tool(self, provider_name: str, tool_name: str) -> Callable[..., BaseTool]:
        provider = self.get_provider(provider_name)
        if provider is None:
            return None
        return provider.get_tool(tool_name)

    def _init_provider_map(self):
        if self.provider_map:
            return

        # 读取 ./provoder.yaml 文件
        current_dir = path.dirname(path.abspath(__file__))
        providers_file_path = path.join(current_dir, "providers.yaml")
        with open(providers_file_path, encoding="utf-8") as f:
            providers_file_data = yaml.safe_load(f)

        for index, provider_data in enumerate(providers_file_data):
            provider_entity = ProviderEntity(**provider_data)
            name = provider_entity.name
            provider = Provider(
                name=name,
                position=index + 1,
                provider_entity=provider_entity,
            )
            self.provider_map[name] = provider

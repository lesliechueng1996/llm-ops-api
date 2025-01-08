"""
@Time   : 2025/01/08 22:28
@Author : Leslie
@File   : builtin_app_manager.py
"""

import os
from injector import inject, singleton
from pydantic import BaseModel, Field
import yaml

from internal.core.builtin_apps.entities.builtin_app_entity import BuiltinAppEntity
from internal.core.builtin_apps.entities.category_entity import CategoryEntity


@inject
@singleton
class BuiltinAppManager(BaseModel):
    builtin_app_map: dict[str, BuiltinAppEntity] = Field(default_factory=dict)
    categories: list[CategoryEntity] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_categories()
        self._init_builtin_app_map()

    def _init_categories(self):
        if self.categories:
            return

        current_path = os.path.abspath(__file__)
        parent_path = os.path.dirname(current_path)
        categories_yaml_path = os.path.join(
            parent_path, "categories", "categories.yaml"
        )

        with open(categories_yaml_path, encoding="utf-8") as f:
            categories = yaml.safe_load(f)

        for category in categories:
            self.categories.append(CategoryEntity(**category))

    def _init_builtin_app_map(self):
        if self.builtin_app_map:
            return

        current_path = os.path.abspath(__file__)
        parent_path = os.path.dirname(current_path)
        builtin_apps_yaml_path = os.path.join(parent_path, "builtin_apps")

        for filename in os.listdir(builtin_apps_yaml_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = os.path.join(builtin_apps_yaml_path, filename)

                with open(filepath, encoding="utf-8") as f:
                    builtin_app = yaml.safe_load(f)

                builtin_app_entity = BuiltinAppEntity(**builtin_app)
                self.builtin_app_map[builtin_app.get("id")] = builtin_app_entity

    def get_categories(self):
        return self.categories

    def get_builtin_app(self, builtin_app_id: str):
        return self.builtin_app_map.get(builtin_app_id, None)

    def get_builtin_apps(self):
        return [
            builtin_app_entity for builtin_app_entity in self.builtin_app_map.values()
        ]

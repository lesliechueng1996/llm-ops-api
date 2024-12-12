"""
@Time   : 2024/12/12 22:56
@Author : Leslie
@File   : builtin_category_manager.py
"""

from pydantic import BaseModel, Field
from typing import Any
from os import path
import yaml
from internal.core.tools.builtin_tools.entities import CategoryEntity
from injector import inject, singleton


@inject
@singleton
class BuiltinCategoryManager(BaseModel):
    category_map: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_categories()

    def _init_categories(self):
        if self.category_map:
            return

        current_dir = path.dirname(path.abspath(__file__))
        categories_file_path = path.join(current_dir, "categories.yaml")
        with open(categories_file_path, encoding="utf-8") as f:
            categories_data = yaml.safe_load(f)

        for category_data in categories_data:
            category_entity = CategoryEntity(**category_data)
            icon_path = path.join(current_dir, "icons", category_entity.icon)
            with open(icon_path, encoding="utf-8") as f:
                icon_data = f.read()

            self.category_map[category_entity.category] = {
                "entity": category_entity,
                "icon": icon_data,
            }

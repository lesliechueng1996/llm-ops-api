"""
@Time   : 2025/01/08 22:07
@Author : Leslie
@File   : category_entity.py
"""

from pydantic import BaseModel, Field


class CategoryEntity(BaseModel):
    category: str = Field(default="")
    name: str = Field(default="")

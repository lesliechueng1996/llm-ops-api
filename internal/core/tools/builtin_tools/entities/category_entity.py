"""
@Time   : 2024/12/12 23:01
@Author : Leslie
@File   : category_entity.py
"""

from pydantic import BaseModel, field_validator

from internal.exception import FailException


class CategoryEntity(BaseModel):
    category: str
    name: str
    icon: str

    @field_validator("icon")
    def check_icon_extension(cls, value: str):
        if not value.endswith(".svg"):
            raise FailException("分类图标只支持svg格式")
        return value

"""
@Time   : 2024/12/12 15:31
@Author : Leslie
@File   : tool_entity.py
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum


class ToolParamType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"


class ToolParamEntity(BaseModel):
    name: str
    label: str
    description: Optional[str] = None
    type: ToolParamType
    default: Optional[Any] = None
    required: bool = False
    min: Optional[float] = None
    max: Optional[float] = None
    options: list[dict[str, Any]] = Field(default_factory=list)


class ToolEntity(BaseModel):
    name: str
    label: str
    description: str
    params: list[ToolParamEntity] = Field(default_factory=list)

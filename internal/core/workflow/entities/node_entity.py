"""
@Time   : 2025/01/09 22:20
@Author : Leslie
@File   : node_entity.py
"""

from enum import Enum
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class BaseNodeData(BaseModel):
    id: UUID
    title: str = ""
    description: str = ""


class NodeStatus(str, Enum):
    RUNNING = "running"
    SUCCESSED = "successed"
    FAILED = "failed"


class NodeResult(BaseModel):
    node_data: BaseNodeData
    status: NodeStatus = NodeStatus.RUNNING
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    error: str = ""

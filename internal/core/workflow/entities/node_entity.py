"""
@Time   : 2025/01/09 22:20
@Author : Leslie
@File   : node_entity.py
"""

from enum import Enum
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    START = "start"
    END = "end"
    LLM = "llm"
    CODE = "code"
    DATASET_RETRIEVAL = "dataset_retrieval"
    HTTP_REQUEST = "http_request"
    TEMPLATE_TRANSFORM = "template_transform"
    TOOL = "tool"


class BaseNodeData(BaseModel):
    id: UUID
    node_type: NodeType
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

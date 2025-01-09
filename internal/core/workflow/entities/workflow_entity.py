"""
@Time   : 2025/01/09 22:17
@Author : Leslie
@File   : workflow_entity.py
"""

from typing import Any, TypedDict, Annotated
from pydantic import BaseModel, Field

from internal.core.workflow.entities.node_entity import NodeResult


def _process_dict(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left = left or {}
    right = right or {}

    return {**left, **right}


def _process_node_list(
    left: list[NodeResult], right: list[NodeResult]
) -> list[NodeResult]:
    left = left or []
    right = right or []

    return left + right


class WorkflowConfig(BaseModel):
    name: str = ""
    description: str = ""
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)


class WorkflowState(TypedDict):
    inputs: Annotated[dict[str, Any], _process_dict]
    outputs: Annotated[dict[str, Any], _process_dict]
    node_results: Annotated[list[NodeResult], _process_node_list]

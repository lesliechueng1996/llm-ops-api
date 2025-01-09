"""
@Time   : 2025/01/09 23:01
@Author : Leslie
@File   : end_entity.py
"""

from pydantic import Field
from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity


class EndNodeData(BaseNodeData):
    outputs: list[VariableEntity] = Field(default_factory=list)

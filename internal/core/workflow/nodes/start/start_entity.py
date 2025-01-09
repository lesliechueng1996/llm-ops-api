"""
@Time   : 2025/01/09 22:40
@Author : Leslie
@File   : start_entity.py
"""

from pydantic import Field
from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import VariableEntity


class StartNodeData(BaseNodeData):
    inputs: list[VariableEntity] = Field(default_factory=list)

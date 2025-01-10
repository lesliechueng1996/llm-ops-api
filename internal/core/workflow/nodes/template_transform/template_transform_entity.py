"""
@Time   : 2025/01/10 23:07
@Author : Leslie
@File   : template_transform_entity.py
"""

from pydantic import Field
from internal.core.workflow.entities.node_entity import BaseNodeData
from internal.core.workflow.entities.variable_entity import (
    VariableEntity,
    VariableValueType,
)


class TemplateTransformNodeData(BaseNodeData):
    template: str = ""
    inputs: list[VariableEntity] = Field(default_factory=list)
    outputs: list[VariableEntity] = Field(
        default_factory=lambda: [
            VariableEntity(
                name="output",
                value={
                    "type": VariableValueType.GENERATED,
                },
            )
        ],
        exclude=True,
    )

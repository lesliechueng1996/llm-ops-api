"""
@Time   : 2025/01/10 22:38
@Author : Leslie
@File   : llm_entity.py
"""

from typing import Any
from internal.core.workflow.entities.node_entity import BaseNodeData
from pydantic import Field

from internal.core.workflow.entities.variable_entity import (
    VariableEntity,
    VariableValueType,
)
from internal.entity.app_entity import DEFAULT_APP_CONFIG


class LLMNodeData(BaseNodeData):
    prompt: str = ""
    language_model_config: dict[str, Any] = Field(
        alias="model_config",
        default_factory=lambda: DEFAULT_APP_CONFIG["model_config"],
    )
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

"""
@Time   : 2025/01/09 22:41
@Author : Leslie
@File   : variable_entity.py
"""

from enum import Enum
from typing import Any, Union
from uuid import UUID

from pydantic import BaseModel, Field


class VariableType(str, Enum):
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "boolean"


VariableTypeMap = {
    VariableType.STRING: str,
    VariableType.INT: int,
    VariableType.FLOAT: float,
    VariableType.BOOLEAN: bool,
}


VariableTypeDefaultValueMap = {
    VariableType.STRING: "",
    VariableType.INT: 0,
    VariableType.FLOAT: 0.0,
    VariableType.BOOLEAN: False,
}


class VariableValueType(str, Enum):
    REF = "ref"
    LITERAL = "literal"
    GENERATED = "generated"


class VariableEntity(BaseModel):

    class Value(BaseModel):

        class Content(BaseModel):
            """记录引用节点id与变量名"""

            ref_node_id: UUID
            ref_var_name: str

        type: VariableValueType = VariableValueType.LITERAL
        content: Union[Content, str, int, float, bool] = ""

    name: str = ""
    description: str = ""
    required: bool = True
    type: VariableType = VariableType.STRING
    value: Value = Field(
        default_factory=lambda: {"type": VariableValueType.LITERAL, "content": ""}
    )

"""
@Time   : 2025/01/09 22:36
@Author : Leslie
@File   : base_node.py
"""

from abc import ABC
from typing import Any
from langchain_core.runnables import RunnableSerializable
from internal.core.workflow.entities.node_entity import BaseNodeData


class BaseNode(RunnableSerializable, ABC):
    _node_data_cls: type[BaseNodeData]
    node_data: BaseNodeData

    def __init__(self, *args: Any, node_data: dict[str, Any], **kwargs: Any):
        super().__init__(*args, node_data=self._node_data_cls(**node_data), **kwargs)

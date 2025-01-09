"""
@Time   : 2025/01/09 22:48
@Author : Leslie
@File   : start_node.py
"""

from typing import Optional
from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes.base_node import BaseNode
from .start_entity import StartNodeData
from langchain_core.runnables import RunnableConfig
from internal.exception import FailException
from internal.core.workflow.entities.variable_entity import VariableTypeDefaultValueMap


class StartNode(BaseNode):
    _node_data_cls = StartNodeData

    def invoke(
        self, state: WorkflowState, config: Optional[RunnableConfig] = None
    ) -> WorkflowState:
        node_data: StartNodeData = self.node_data
        inputs = node_data.inputs
        outputs = {}

        for input in inputs:
            input_value = state["inputs"].get(input.name, None)
            if input.required and input_value is None:
                raise FailException(f"工作流参数生成一场: {input.name} 为必填参数")
            if not input.required and input_value is None:
                input_value = VariableTypeDefaultValueMap[input.type]

            outputs[input.name] = input_value

        return {
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.SUCCESSED,
                    inputs=state["inputs"],
                    outputs=outputs,
                )
            ]
        }

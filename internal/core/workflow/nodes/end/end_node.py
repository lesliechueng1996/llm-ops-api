"""
@Time   : 2025/01/09 23:02
@Author : Leslie
@File   : end_node.py
"""

from typing import Optional
from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.variable_entity import (
    VariableValueType,
    VariableTypeDefaultValueMap,
)
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes.base_node import BaseNode
from internal.core.workflow.nodes.end.end_entity import EndNodeData
from langchain_core.runnables import RunnableConfig


class EndNode(BaseNode):
    _node_data_cls = EndNodeData

    def invoke(
        self, state: WorkflowState, config: Optional[RunnableConfig] = None
    ) -> WorkflowState:
        node_data: EndNodeData = self.node_data
        outputs = node_data.outputs

        result = {}

        for output in outputs:
            if output.value.type == VariableValueType.LITERAL:
                result[output.name] = output.value.content
            else:
                for node_result in state["node_results"]:
                    if node_result.node_data.id == output.value.content.ref_node_id:
                        result[output.name] = node_result.outputs.get(
                            output.value.content.ref_var_name,
                            VariableTypeDefaultValueMap[output.type],
                        )
                        break

        return {
            "outputs": result,
            "node_results": [
                NodeResult(
                    node_data=self.node_data,
                    status=NodeStatus.SUCCESSED,
                    inputs={},
                    outputs=result,
                )
            ],
        }

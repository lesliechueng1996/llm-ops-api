"""
@Time   : 2025/01/10 23:09
@Author : Leslie
@File   : template_transform_node.py
"""

from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.variable_entity import (
    VariableValueType,
    VariableTypeDefaultValueMap,
)
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes.base_node import BaseNode
from internal.core.workflow.nodes.template_transform.template_transform_entity import (
    TemplateTransformNodeData,
)
from jinja2 import Template


class TemplateTransformNode(BaseNode):
    _node_data_cls: TemplateTransformNodeData

    def invoke(self, state: WorkflowState, config=None, **kwargs) -> WorkflowState:
        node_data: TemplateTransformNodeData = self.node_data
        inputs = node_data.inputs

        inputs_dict = {}
        for input in inputs:
            if input.value.type == VariableValueType.LITERAL:
                inputs_dict[input.name] = input.value.content
            else:
                for node_result in state["node_results"]:
                    if node_result.node_data.id == input.value.content.ref_node_id:
                        inputs_dict[input.name] = node_result.outputs.get(
                            input.value.content.ref_var_name,
                            VariableTypeDefaultValueMap[input.type],
                        )
        template = Template(node_data.template)
        template_value = template.render(**inputs_dict)

        outputs_dict = {}
        if node_data.outputs:
            outputs_dict[node_data.outputs[0].name] = template_value
        else:
            outputs_dict["output"] = template_value

        return {
            "node_results": [
                NodeResult(
                    node_data=node_data,
                    status=NodeStatus.SUCCESSED,
                    inputs=inputs_dict,
                    outputs=outputs_dict,
                )
            ]
        }

"""
@Time   : 2025/01/10 22:44
@Author : Leslie
@File   : llm_node.py
"""

from os import getenv
from internal.core.workflow.entities.node_entity import NodeResult, NodeStatus
from internal.core.workflow.entities.variable_entity import (
    VariableValueType,
    VariableTypeDefaultValueMap,
)
from internal.core.workflow.entities.workflow_entity import WorkflowState
from internal.core.workflow.nodes import BaseNode
from internal.core.workflow.nodes.llm.llm_entity import LLMNodeData
from jinja2 import Template
from langchain_openai import ChatOpenAI


class LLMNode(BaseNode):
    _node_data_cls: LLMNodeData

    def invoke(self, state: WorkflowState, config=None, **kwargs) -> WorkflowState:
        node_data: LLMNodeData = self.node_data
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
        template = Template(self.node_data.prompt)
        prompt_value = template.render(**inputs_dict)

        llm = ChatOpenAI(
            model=self.node_data.language_model_config.get("model", "gpt-4o-mini"),
            **self.node_data.language_model_config.get("parameters", {}),
            api_key=getenv("OPENAI_KEY"),
            base_url=getenv("OPENAI_API_URL"),
        )

        content = llm.invoke(prompt_value).content

        outputs_dict = {}
        if node_data.outputs:
            outputs_dict[node_data.outputs[0].name] = content
        else:
            outputs_dict["output"] = content

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

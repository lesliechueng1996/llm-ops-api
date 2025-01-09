"""
@Time   : 2025/01/09 22:15
@Author : Leslie
@File   : workflow.py
"""

from typing import Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig

from internal.core.workflow.entities.node_entity import NodeType
from internal.core.workflow.entities.variable_entity import (
    VariableEntity,
    VariableTypeMap,
)
from .entities.workflow_entity import WorkflowConfig, WorkflowState
from pydantic import BaseModel, Field, PrivateAttr, create_model
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph
from langchain_core.runnables.utils import Input
from .nodes import StartNode, EndNode


class Workflow(BaseTool):

    _workflow_config: WorkflowConfig = PrivateAttr(None)
    _workflow: CompiledStateGraph = PrivateAttr(None)

    def __init__(self, workflow_config: WorkflowConfig, **kwargs: Any):
        super().__init__(
            name=workflow_config.name,
            description=workflow_config.description,
            args_schema=self._build_args_schema(workflow_config),
            **kwargs,
        )

        self._workflow_config = workflow_config
        self._workflow = self._build_workflow()

    @classmethod
    def _build_args_schema(cls, workflow_config: WorkflowConfig) -> type[BaseModel]:
        inputs: list[VariableEntity] = next(
            (
                node.get("inputs", [])
                for node in workflow_config.nodes
                if node.get("node_type") == NodeType.Start
            ),
            [],
        )

        fields = {}
        for input in inputs:
            field_name = input.get("name")
            field_type = VariableTypeMap.get(input.get("type"), str)
            field_required = input.get("required", True)
            field_description = input.get("description", "")

            fields[field_name] = (
                field_type if field_required else Optional[field_type],
                Field(description=field_description),
            )

        return create_model("DynamicModel", **fields)

    def _build_workflow(self):
        graph = StateGraph(WorkflowState)

        nodes = self._workflow_config.nodes
        edges = self._workflow_config.edges

        for node in nodes:
            if node.get("node_type") == NodeType.START:
                graph.add_node(
                    f"{NodeType.START.value}_{node.get('id')}",
                    StartNode(node_data=node),
                )
            elif node.get("node_type") == NodeType.END:
                graph.add_node(
                    f"{NodeType.END.value}_{node.get('id')}",
                    EndNode(node_data=node),
                )

        for edge in edges:
            from_node = f"{edge.get('source_type')}_{edge.get('source')}"
            to_node = f"{edge.get('target_type')}_{edge.get('target')}"

            graph.add_edge(from_node, to_node)

            if edge.get("source_type") == NodeType.START:
                graph.set_entry_point(from_node)
            elif edge.get("target_type") == NodeType.END:
                graph.set_exit_point(to_node)

        return graph.compile()

    def _run(self, *args, **kwargs):
        return self._workflow.invoke({"inputs": kwargs})

    def stream(self, input: Input, config: Optional[RunnableConfig] = None, **kwargs):
        return self._workflow.stream({"inputs": input})

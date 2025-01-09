"""
@Time   : 2025/01/09 22:15
@Author : Leslie
@File   : workflow.py
"""

from typing import Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from .entities.workflow_entity import WorkflowConfig, WorkflowState
from pydantic import PrivateAttr
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph
from langchain_core.runnables.utils import Input


class Workflow(BaseTool):

    _workflow_config: WorkflowConfig = PrivateAttr(None)
    _workflow: CompiledStateGraph = PrivateAttr(None)

    def __init__(self, workflow_config: WorkflowConfig, **kwargs: Any):
        super().__init__(
            name=workflow_config.name,
            description=workflow_config.description,
            **kwargs,
        )

        self._workflow_config = workflow_config
        self._workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(WorkflowState)

        return graph.compile()

    def _run(self, *args, **kwargs):
        return self._workflow.invoke({"inputs": kwargs})

    def stream(self, input: Input, config: Optional[RunnableConfig] = None, **kwargs):
        return self._workflow.stream({"inputs": input})

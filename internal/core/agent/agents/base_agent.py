"""
@Time   : 2024/12/23 22:35
@Author : Leslie
@File   : base_agent.py
"""

from abc import abstractmethod
from threading import Thread
from typing import Iterator, Optional
from uuid import uuid4
from internal.core.agent.entities import AgentConfig
from langchain_core.messages import AnyMessage

from internal.core.agent.entities.agent_entity import AgentState
from internal.core.agent.entities.queue_entity import AgentResult, AgentThought
from internal.exception.exception import FailException
from .agent_queue_manager import AgentQueueManager
from langchain_core.runnables import Runnable
from langchain_core.load import Serializable
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables import RunnableConfig
from pydantic import PrivateAttr


class BaseAgent(Serializable, Runnable):
    llm: BaseLanguageModel
    agent_config: AgentConfig
    _agent_queue_manager: AgentQueueManager = PrivateAttr(None)
    _agent: CompiledStateGraph = PrivateAttr(None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        llm: BaseLanguageModel,
        agent_config: AgentConfig,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args, llm=llm, agent_config=agent_config, name="test", **kwargs
        )
        self._agent = self._build_agent()
        self._agent_queue_manager = AgentQueueManager(
            user_id=agent_config.user_id,
            invoke_from=agent_config.invoke_from,
        )

    @abstractmethod
    def _build_agent(self) -> CompiledStateGraph:
        raise NotImplementedError("Agent智能体的_build_agent函数未实现")

    def invoke(
        self, input: AgentState, config: Optional[RunnableConfig] = None
    ) -> AgentResult:
        pass

    def stream(
        self, input: AgentState, config: Optional[RunnableConfig] = None, **kwargs
    ) -> Iterator[AgentThought]:
        if not self._agent:
            raise FailException("Agent智能体未初始化")

        input["task_id"] = input.get("task_id", uuid4())
        input["history"] = input.get("history", [])
        input["iteration_count"] = input.get("iteration_count", 0)

        thread = Thread(target=self._agent.invoke, args=(input,))
        thread.start()

        yield from self._agent_queue_manager.listen(task_id=input["task_id"])

    @property
    def agent_queue_manager(self) -> AgentQueueManager:
        return self._agent_queue_manager

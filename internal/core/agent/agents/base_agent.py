"""
@Time   : 2024/12/23 22:35
@Author : Leslie
@File   : base_agent.py
"""

from abc import ABC, abstractmethod
from internal.core.agent.entities import AgentConfig
from langchain_core.messages import AnyMessage


class BaseAgent(ABC):

    agent_config: AgentConfig

    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config

    @abstractmethod
    def run(
        self, query: str, history: list[AnyMessage] = None, long_term_memory: str = None
    ):
        raise NotImplementedError("Agent智能体的run函数未实现")

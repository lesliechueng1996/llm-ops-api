"""
@Time   : 2024/12/24 14:28
@Author : Leslie
@File   : queue_entity.py
"""

from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field

from internal.entity.conversation_entity import MessageStatus


class QueueEvent(str, Enum):
    LONG_TERM_MEMORY_RECALL = "long_term_memory_recall"  # 长期记忆召回事件
    AGENT_THOUGHT = "agent_thought"  # agent观察事件
    AGENT_MESSAGE = "agent_message"  # agent消息事件
    AGENT_ACTION = "agent_action"  # agent行为事件
    DATASET_RETRIEVAL = "dataset_retrieval"  # 知识集检索事件
    AGENT_END = "agent_end"  # agent结束事件
    STOP = "stop"  # 停止事件
    ERROR = "error"  # 错误事件
    TIMEOUT = "timeout"  # 超时事件
    PING = "ping"  # ping事件


class AgentThought(BaseModel):
    id: UUID
    task_id: UUID

    event: QueueEvent
    thought: str = ""
    observation: str = ""

    tool: str = ""
    tool_input: dict = Field(default_factory=dict)

    message: list[dict] = Field(default_factory=list)
    message_token_count: int = 0
    message_unit_price: float = 0
    message_price_unit: float = 0

    answer: str = ""
    answer_token_count: int = 0
    answer_unit_price: float = 0
    answer_price_unit: float = 0

    total_token_count: int = 0
    total_price: float = 0
    latency: float = 0


class AgentResult(BaseModel):
    query: str

    message: list[dict] = Field(default_factory=list)
    message_token_count: int = 0
    message_unit_price: float = 0
    message_price_unit: float = 0

    answer: str = ""
    answer_token_count: int = 0
    answer_unit_price: float = 0
    answer_price_unit: float = 0

    total_token_count: int = 0
    total_price: float = 0
    latency: float = 0

    status: str = MessageStatus.NORMAL
    error: str = ""

    agent_thoughts: list[AgentThought] = Field(default_factory=list)

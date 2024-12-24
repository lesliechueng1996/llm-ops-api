"""
@Time   : 2024/12/23 22:38
@Author : Leslie
@File   : function_call_agent.py
"""

import json
import time
from threading import Thread
from internal.core.agent.agents.base_agent import BaseAgent
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    RemoveMessage,
    ToolMessage,
    messages_to_dict,
)
from typing import Literal
from internal.core.agent.entities import (
    AgentState,
    AGENT_SYSTEM_PROMPT_TEMPLATE,
    AgentQueueEvent,
    QueueEvent,
)
from langgraph.graph import START, END, StateGraph
from internal.exception import FailException
from uuid import uuid4


class FunctionCallAgent(BaseAgent):
    def run(
        self, query: str, history: list[AnyMessage] = None, long_term_memory: str = None
    ):
        if history is None:
            history = []

        agent = self._build_graph()

        thread = Thread(
            target=agent.invoke,
            args=(
                {
                    "messages": [HumanMessage(content=query)],
                    "history": history,
                    "long_term_memory": long_term_memory,
                },
            ),
        )
        thread.start()

        yield from self.agent_queue_manager.listen()
        # return agent.invoke(
        #     {
        #         "messages": [HumanMessage(content=query)],
        #         "history": history,
        #         "long_term_memory": long_term_memory,
        #     }
        # )

    def _build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("long_term_memory_recall", self._long_term_memory_recall_node)
        graph.add_node("llm", self._llm_node)
        graph.add_node("tools", self._tools_node)

        graph.add_edge(START, "long_term_memory_recall")
        graph.add_edge("long_term_memory_recall", "llm")
        graph.add_conditional_edges("llm", self._tools_condition)
        graph.add_edge("tools", "llm")

        return graph.compile()

    def _long_term_memory_recall_node(self, state: AgentState) -> AgentState:
        long_term_memory = ""
        if self.agent_config.enable_long_term_memory:
            long_term_memory = state["long_term_memory"]
            self.agent_queue_manager.publish(
                AgentQueueEvent(
                    id=uuid4(),
                    task_id=self.agent_queue_manager.task_id,
                    event=QueueEvent.LONG_TERM_MEMORY_RECALL,
                    observation=long_term_memory,
                )
            )

        preset_messages = [
            SystemMessage(
                AGENT_SYSTEM_PROMPT_TEMPLATE.format(
                    preset_prompt=self.agent_config.preset_prompt,
                    long_term_memory=long_term_memory,
                )
            )
        ]

        history = state["history"]
        if isinstance(history, list) and len(history) > 0:
            if len(history) % 2 != 0:
                raise FailException("智能体历史消息列表格式错误")
            preset_messages.extend(history)

        human_message = state["messages"][-1]
        preset_messages.append(HumanMessage(content=human_message.content))

        return {
            "messages": [RemoveMessage(id=human_message.id), *preset_messages],
        }

    def _llm_node(self, state: AgentState) -> AgentState:
        llm = self.agent_config.llm
        start_at = time.perf_counter()
        id = uuid4()

        if (
            hasattr(llm, "bind_tools")
            and callable(getattr(llm, "bind_tools"))
            and len(self.agent_config.tools) > 0
        ):
            llm = llm.bind_tools(self.agent_config.tools)

        chunks = llm.stream(state["messages"])

        is_first_chunk = True
        gathered = None
        generation_type = ""
        for chunk in chunks:
            if is_first_chunk:
                gathered = chunk
                is_first_chunk = False
            else:
                gathered += chunk

            if not generation_type:
                if chunk.tool_calls:
                    generation_type = "thought"
                elif chunk.content:
                    generation_type = "message"

            if generation_type == "message":
                self.agent_queue_manager.publish(
                    AgentQueueEvent(
                        id=id,
                        task_id=self.agent_queue_manager.task_id,
                        event=QueueEvent.AGENT_MESSAGE,
                        thought=chunk.content,
                        messages=messages_to_dict(state["messages"]),
                        answer=chunk.content,
                        latency=time.perf_counter() - start_at,
                    )
                )

        if generation_type == "thought":
            self.agent_queue_manager.publish(
                AgentQueueEvent(
                    id=id,
                    task_id=self.agent_queue_manager.task_id,
                    event=QueueEvent.AGENT_THOUGHT,
                    messages=messages_to_dict(state["messages"]),
                    latency=time.perf_counter() - start_at,
                )
            )

        if generation_type == "message":
            self.agent_queue_manager.stop_listen()

        return {"messages": [gathered]}

    def _tools_node(self, state: AgentState) -> AgentState:
        tools_by_name = {tool.name: tool for tool in self.agent_config.tools}

        ai_message = state["messages"][-1]
        tool_calls = ai_message.tool_calls

        tool_messages = []
        for tool_call in tool_calls:
            id = uuid4()
            start_at = time.perf_counter()

            tool = tools_by_name[tool_call["name"]]
            result = tool.invoke(tool_call["args"])
            tool_messages.append(
                ToolMessage(
                    content=json.dumps(result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

            event = (
                QueueEvent.AGENT_ACTION
                if tool_call["name"] != "dataset_retrieval"
                else QueueEvent.DATASET_RETRIEVAL
            )

            self.agent_queue_manager.publish(
                AgentQueueEvent(
                    id=id,
                    task_id=self.agent_queue_manager.task_id,
                    event=event,
                    observation=json.dumps(result),
                    tool=tool_call["name"],
                    tool_input=tool_call["args"],
                    latency=time.perf_counter() - start_at,
                )
            )

        return {"messages": tool_messages}

    def _tools_condition(self, state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        ai_message = messages[-1]
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

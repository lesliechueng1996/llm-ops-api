"""
@Time   : 2024/12/23 22:38
@Author : Leslie
@File   : function_call_agent.py
"""

import json
from threading import Thread
from internal.core.agent.agents.base_agent import BaseAgent
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    RemoveMessage,
    ToolMessage,
)
from typing import Literal
from internal.core.agent.entities.agent_entity import (
    AgentState,
    AGENT_SYSTEM_PROMPT_TEMPLATE,
)
from langgraph.graph import START, END, StateGraph
from internal.exception import FailException


class FunctionCallAgent(BaseAgent):
    def run(
        self, query: str, history: list[AnyMessage] = None, long_term_memory: str = None
    ):
        if history is None:
            history = []

        agent = self._build_graph()

        # thread = Thread(
        #     target=agent.invoke,
        #     args=(
        #         {
        #             "messages": [HumanMessage(content=query)],
        #             "history": history,
        #             "long_term_memory": long_term_memory,
        #         },
        #     ),
        # )
        # thread.start()
        return agent.invoke(
            {
                "messages": [HumanMessage(content=query)],
                "history": history,
                "long_term_memory": long_term_memory,
            }
        )

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

        if (
            hasattr(llm, "bind_tools")
            and callable(getattr(llm, "bind_tools"))
            and len(self.agent_config.tools) > 0
        ):
            llm = llm.bind_tools(self.agent_config.tools)

        chunks = llm.stream(state["messages"])

        is_first_chunk = True
        gathered = None

        for chunk in chunks:
            if is_first_chunk:
                gathered = chunk
                is_first_chunk = False
            else:
                gathered += chunk

        return {"messages": [gathered]}

    def _tools_node(self, state: AgentState) -> AgentState:
        tools_by_name = {tool.name: tool for tool in self.agent_config.tools}

        ai_message = state["messages"][-1]
        tool_calls = ai_message.tool_calls

        tool_messages = []
        for tool_call in tool_calls:
            tool = tools_by_name[tool_call["name"]]
            result = tool.invoke(tool_call["args"])
            tool_messages.append(
                ToolMessage(
                    content=json.dumps(result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": tool_messages}

    def _tools_condition(self, state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        ai_message = messages[-1]
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

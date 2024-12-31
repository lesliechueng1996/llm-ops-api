"""
@Time   : 2024/12/23 22:38
@Author : Leslie
@File   : function_call_agent.py
"""

import json
import logging
import re
import time
from internal.core.agent.agents.base_agent import BaseAgent
from langchain_core.messages import (
    AIMessage,
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
    AgentThought,
    QueueEvent,
    DATASET_RETRIEVAL_TOOL_NAME,
)
from langgraph.graph import START, END, StateGraph
from internal.core.agent.entities.agent_entity import MAX_ITERATION_RESPONSE
from internal.exception import FailException
from uuid import uuid4


class FunctionCallAgent(BaseAgent):
    def _build_agent(self):
        graph = StateGraph(AgentState)

        graph.add_node("preset_operation", self._preset_operation_node)
        graph.add_node("long_term_memory_recall", self._long_term_memory_recall_node)
        graph.add_node("llm", self._llm_node)
        graph.add_node("tools", self._tools_node)

        graph.add_edge(START, "preset_operation")
        graph.add_conditional_edges(
            "preset_operation", self._preset_operation_condition
        )
        graph.add_edge("long_term_memory_recall", "llm")
        graph.add_conditional_edges("llm", self._tools_condition)
        graph.add_edge("tools", "llm")

        return graph.compile()

    def _preset_operation_node(self, state: AgentState) -> AgentState:
        review_config = self.agent_config.review_config
        query = state["messages"][-1].content

        if review_config["enable"] and review_config["inputs_config"]["enable"]:
            contains_keywords = any(
                keyword in query for keyword in review_config["keywords"]
            )
            if contains_keywords:
                preset_response = review_config["inputs_config"]["preset_response"]
                self.agent_queue_manager.publish(
                    AgentThought(
                        id=uuid4(),
                        task_id=state["task_id"],
                        event=QueueEvent.AGENT_MESSAGE,
                        thought=preset_response,
                        message=messages_to_dict(state["messages"]),
                        answer=preset_response,
                        latency=0,
                    ),
                    state["task_id"],
                )
                self.agent_queue_manager.publish(
                    AgentThought(
                        id=uuid4(),
                        task_id=state["task_id"],
                        event=QueueEvent.AGENT_END,
                    ),
                    state["task_id"],
                )

                return {"messages": [AIMessage(content=preset_response)]}
        return {"messages": []}

    def _long_term_memory_recall_node(self, state: AgentState) -> AgentState:
        long_term_memory = ""
        if self.agent_config.enable_long_term_memory:
            long_term_memory = state["long_term_memory"]
            self.agent_queue_manager.publish(
                AgentThought(
                    id=uuid4(),
                    task_id=state["task_id"],
                    event=QueueEvent.LONG_TERM_MEMORY_RECALL,
                    observation=long_term_memory,
                ),
                state["task_id"],
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
                self.agent_queue_manager.publish_error(
                    state["task_id"], "智能体历史消息列表格式错误"
                )
                logging.error(
                    f"智能体历史消息列表格式错误, len(history)={len(history)}, history={json.dumps(messages_to_dict(history))}"
                )
                raise FailException("智能体历史消息列表格式错误")
            preset_messages.extend(history)

        human_message = state["messages"][-1]
        preset_messages.append(HumanMessage(content=human_message.content))

        return {
            "messages": [RemoveMessage(id=human_message.id), *preset_messages],
        }

    def _llm_node(self, state: AgentState) -> AgentState:
        if state["iteration_count"] >= self.agent_config.max_iteration_count:
            self.agent_queue_manager.publish(
                AgentThought(
                    id=uuid4(),
                    task_id=state["task_id"],
                    event=QueueEvent.AGENT_MESSAGE,
                    thought=MAX_ITERATION_RESPONSE,
                    message=messages_to_dict(state["messages"]),
                    answer=MAX_ITERATION_RESPONSE,
                    latency=0,
                ),
                state["task_id"],
            )
            self.agent_queue_manager.publish(
                AgentThought(
                    id=uuid4(),
                    task_id=state["task_id"],
                    event=QueueEvent.AGENT_END,
                ),
                state["task_id"],
            )
            return {"messages": [AIMessage(content=MAX_ITERATION_RESPONSE)]}

        llm = self.llm
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
                review_config = self.agent_config.review_config
                content = chunk.content

                if (
                    review_config["enable"]
                    and review_config["outputs_config"]["enable"]
                ):
                    for keyword in review_config["keywords"]:
                        content = re.sub(
                            re.escape(keyword), "**", content, flags=re.IGNORECASE
                        )

                self.agent_queue_manager.publish(
                    AgentThought(
                        id=id,
                        task_id=state["task_id"],
                        event=QueueEvent.AGENT_MESSAGE,
                        thought=content,
                        message=messages_to_dict(state["messages"]),
                        answer=content,
                        latency=time.perf_counter() - start_at,
                    ),
                    state["task_id"],
                )

        if generation_type == "thought":
            self.agent_queue_manager.publish(
                AgentThought(
                    id=id,
                    task_id=state["task_id"],
                    event=QueueEvent.AGENT_THOUGHT,
                    thought=json.dumps(gathered.tool_calls),
                    message=messages_to_dict(state["messages"]),
                    latency=time.perf_counter() - start_at,
                ),
                state["task_id"],
            )

        if generation_type == "message":
            self.agent_queue_manager.publish(
                AgentThought(
                    id=uuid4(),
                    task_id=state["task_id"],
                    event=QueueEvent.AGENT_END,
                ),
                state["task_id"],
            )

        return {"messages": [gathered], "iteration_count": state["iteration_count"] + 1}

    def _tools_node(self, state: AgentState) -> AgentState:
        tools_by_name = {tool.name: tool for tool in self.agent_config.tools}

        ai_message = state["messages"][-1]
        tool_calls = ai_message.tool_calls

        tool_messages = []
        try:
            for tool_call in tool_calls:
                id = uuid4()
                start_at = time.perf_counter()

                try:
                    tool = tools_by_name[tool_call["name"]]
                    result = tool.invoke(tool_call["args"])
                except Exception as e:
                    result = f"工具执行出错：{str(e)}"

                tool_messages.append(
                    ToolMessage(
                        content=json.dumps(result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    )
                )

                event = (
                    QueueEvent.AGENT_ACTION
                    if tool_call["name"] != DATASET_RETRIEVAL_TOOL_NAME
                    else QueueEvent.DATASET_RETRIEVAL
                )

                self.agent_queue_manager.publish(
                    AgentThought(
                        id=id,
                        task_id=state["task_id"],
                        event=event,
                        observation=json.dumps(result),
                        tool=tool_call["name"],
                        tool_input=tool_call["args"],
                        latency=time.perf_counter() - start_at,
                    ),
                    state["task_id"],
                )
        except Exception as e:
            logging.exception(f"LLM节点发生错误, 错误信息: {str(e)}")
            self.agent_queue_manager.publish_error(
                state["task_id"], f"LLM节点发生错误, 错误信息: {str(e)}"
            )
            raise e
        return {"messages": tool_messages}

    def _tools_condition(self, state: AgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        ai_message = messages[-1]
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    def _preset_operation_condition(
        self, state: AgentState
    ) -> Literal["long_term_memory_recall", "__end__"]:
        message = state["messages"][-1]
        if message.type == "ai":
            return END
        return "long_term_memory_recall"

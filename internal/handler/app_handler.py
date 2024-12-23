"""
@Time   : 2024/12/1 05:28
@Author : Leslie
@File   : app_handler.py
"""

import json
from threading import Thread
from typing import Any, Generator, Literal
from flask import request
import os
from internal.schema import CompletionReq
from internal.service import (
    AppService,
    VectorStoreService,
    JiebaService,
    ConversationService,
)
from pkg.response import (
    validate_error_json,
    success_json,
    success_message,
    compact_generate_response,
)
from injector import inject
from dataclasses import dataclass
from uuid import UUID, uuid4
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.output_parsers.string import StrOutputParser
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.memory import BaseMemory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableConfig
from operator import itemgetter
from langchain_core.tracers.schemas import Run
from internal.core.file_extractor import FileExtractor
from pkg.sqlalchemy import SQLAlchemy
from langgraph.graph import MessagesState, END, START, StateGraph
from langchain_openai import ChatOpenAI
from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from queue import Queue
from langchain_core.messages import ToolMessage


@inject
@dataclass
class AppHandler:
    app_service: AppService
    vector_store_service: VectorStoreService
    # api_tool_service: ApiToolService
    # embedding_service: EmbeddingService
    file_extractor: FileExtractor
    db: SQLAlchemy
    jieba_service: JiebaService
    builtin_provider_manager: BuiltinProviderManager
    conversation_service: ConversationService

    def ping(self):
        from internal.core.agent.agents.function_call_agent import FunctionCallAgent
        from internal.core.agent.entities.agent_entity import AgentConfig

        config = AgentConfig(
            llm=ChatOpenAI(
                api_key=os.getenv("OPENAI_KEY"),
                base_url=os.getenv("OPENAI_API_URL"),
                model="gpt-4o-mini",
            ),
            preset_prompt="你是一个诗人，可以根据用户的输入生成诗歌。",
        )

        agent = FunctionCallAgent(config)

        status = agent.run("程序员")
        print(status["messages"][-1].content)

        return success_message("pong")

    @classmethod
    def _load_memory_variables(cls, input: dict[str, Any], config: RunnableConfig):
        configurable = config.get("configurable", {})
        memory = configurable.get("memory")
        if memory is not None and isinstance(memory, BaseMemory):
            return memory.load_memory_variables(input)
        return {"history": []}

    @classmethod
    def _save_context(cls, run_obj: Run, config: RunnableConfig):
        configurable = config.get("configurable", {})
        memory = configurable.get("memory")
        if memory is not None and isinstance(memory, BaseMemory):
            memory.save_context(run_obj.inputs, run_obj.outputs)

    def debug(self, app_id: UUID):
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        query = req.query.data
        queue = Queue()

        def graph_app() -> None:

            tools = [
                self.builtin_provider_manager.get_tool("google", "google_serper")(),
                self.builtin_provider_manager.get_tool("gaode", "gaode_weather")(),
                self.builtin_provider_manager.get_tool("dalle", "dalle3")(),
            ]

            def chatbot(state: MessagesState) -> MessagesState:
                llm = ChatOpenAI(
                    api_key=os.getenv("OPENAI_KEY"),
                    base_url=os.getenv("OPENAI_API_URL"),
                    model="gpt-4o-mini",
                    temperature=0.7,
                ).bind_tools(tools)

                chunks = llm.stream(state["messages"])

                is_first_chunk = True
                is_tool_call = False
                gathered = None
                id = str(uuid4())
                for chunk in chunks:
                    # Some models may return empty chunk for the first chunk
                    if is_first_chunk and chunk.content == "" and not chunk.tool_calls:
                        continue

                    if is_first_chunk:
                        is_first_chunk = False
                        gathered = chunk
                    else:
                        gathered = gathered + chunk

                    if chunk.tool_calls or is_tool_call:
                        is_tool_call = True
                        queue.put(
                            {
                                "id": id,
                                "event": "agent_thought",
                                "data": json.dumps(
                                    chunk.tool_call_chunks, ensure_ascii=False
                                ),
                            }
                        )
                    else:
                        queue.put(
                            {
                                "id": id,
                                "event": "agent_message",
                                "data": chunk.content,
                            }
                        )
                return {"messages": [gathered]}

            def tool_executor(state: MessagesState) -> MessagesState:
                last_message = state["messages"][-1]
                tool_name_map = {tool.name: tool for tool in tools}

                tool_messages = []
                for tool_call in last_message.tool_calls:
                    tool = tool_name_map[tool_call["name"]]
                    tool_result = tool.invoke(tool_call["args"])
                    tool_messages.append(
                        ToolMessage(
                            content=json.dumps(tool_result, ensure_ascii=False),
                            tool_call_id=tool_call["id"],
                            name=tool_call["name"],
                        )
                    )
                    queue.put(
                        {
                            "id": str(uuid4()),
                            "event": "agent_action",
                            "data": json.dumps(tool_result, ensure_ascii=False),
                        }
                    )
                return {"messages": tool_messages}

            def route(state: MessagesState) -> Literal["__end__", "tool_executor"]:
                last_message = state["messages"][-1]
                if (
                    hasattr(last_message, "tool_calls")
                    and len(last_message.tool_calls) > 0
                ):
                    return "tool_executor"
                return END

            graph_builder = StateGraph(MessagesState)
            graph_builder.add_node("chatbot", chatbot)
            graph_builder.add_node("tool_executor", tool_executor)

            graph_builder.add_edge(START, "chatbot")
            graph_builder.add_conditional_edges("chatbot", route)
            graph_builder.add_edge("tool_executor", "chatbot")

            graph = graph_builder.compile()
            result = graph.invoke({"messages": [("human", query)]})
            print("最终结果", result)
            queue.put(None)

        t = Thread(target=graph_app)
        t.start()

        def stream_event_response() -> Generator:
            while True:
                item = queue.get()
                if item is None:
                    break
                yield f"event: {item.get('event')}\ndata: {json.dumps(item, ensure_ascii=False)}\n\n"
                queue.task_done()

        return compact_generate_response(stream_event_response())

    def _debug(self, app_id: UUID):
        """聊天接口"""
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)
        query = request.json.get("query")

        # 构建 prompt
        system_prompt = "你是一个强大的聊天机器人，能根据对应的上下文和历史对话信息回复用户问题。\n\n<context>{context}</context>"
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("history"),
                ("human", "{query}"),
            ]
        )

        # 构建 Moonshot AI 客户端
        client = MoonshotChat(
            moonshot_api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_URL"),
        )
        memory = ConversationBufferWindowMemory(
            k=3,
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt"),
            return_messages=True,
        )

        # 构建解析器
        str_parser = StrOutputParser()

        retriever = (
            self.vector_store_service.get_retriever()
            | self.vector_store_service.combine_documents
        )
        # 构建链
        chain = (
            RunnablePassthrough.assign(
                context=itemgetter("query") | retriever,
                history=RunnableLambda(self._load_memory_variables)
                | itemgetter(memory.memory_key),
            )
            | prompt
            | client
            | str_parser
        ).with_listeners(on_end=self._save_context)

        human_input = {"query": query}

        # 获取 AI 完成的内容
        content = chain.invoke(
            human_input,
            config={
                "configurable": {
                    "memory": memory,
                }
            },
        )

        return success_json({"content": content})

    def create_app(self):
        app = self.app_service.create_app()
        return success_message(f"创建应用成功, 应用ID: {app.id}")

    def get_app(self, id: UUID):
        app = self.app_service.get_app(id)
        return success_message(f"获取应用成功, 应用名称: {app.name}")

    def update_app(self, id: UUID):
        app = self.app_service.update_app(id)
        return success_message(f"更新应用成功, 应用名称: {app.name}")

    def delete_app(self, id: UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"删除应用成功, 应用ID: {app.id}")

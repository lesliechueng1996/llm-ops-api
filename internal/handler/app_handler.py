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

from redis import Redis
from internal.core.agent.agents.agent_queue_manager import AgentQueueManager
from internal.entity.conversation_entity import InvokeFrom
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
from langchain_openai import ChatOpenAI
from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.core.agent.agents.function_call_agent import FunctionCallAgent
from internal.core.agent.entities.agent_entity import AgentConfig


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
    redis_client: Redis

    def ping(self):
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

        tools = [
            self.builtin_provider_manager.get_tool("google", "google_serper")(),
            self.builtin_provider_manager.get_tool("gaode", "gaode_weather")(),
            self.builtin_provider_manager.get_tool("dalle", "dalle3")(),
        ]

        config = AgentConfig(
            llm=ChatOpenAI(
                api_key=os.getenv("OPENAI_KEY"),
                base_url=os.getenv("OPENAI_API_URL"),
                model="gpt-4o-mini",
            ),
            enable_long_term_memory=True,
            tools=tools,
        )

        agent_queue_manager = AgentQueueManager(
            user_id=uuid4(),
            task_id=uuid4(),
            invoke_from=InvokeFrom.DEBUGGER,
            redis_client=self.redis_client,
        )

        agent = FunctionCallAgent(config, agent_queue_manager)

        def stream_event_response() -> Generator:
            """流式事件输出响应"""
            for agent_queue_event in agent.run(
                req.query.data, [], "用户介绍自己叫慕小课"
            ):
                data = {
                    "id": str(agent_queue_event.id),
                    "task_id": str(agent_queue_event.task_id),
                    "event": agent_queue_event.event,
                    "thought": agent_queue_event.thought,
                    "observation": agent_queue_event.observation,
                    "tool": agent_queue_event.tool,
                    "tool_input": agent_queue_event.tool_input,
                    "answer": agent_queue_event.answer,
                    "latency": agent_queue_event.latency,
                }
                yield f"event: {agent_queue_event.event}\ndata: {json.dumps(data)}\n\n"

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

"""
@Time   : 2024/12/1 05:28
@Author : Leslie
@File   : app_handler.py
"""

from typing import Any
from flask import request
import os
from internal.schema.app_schema import CompletionReq
from internal.service import AppService, VectorStoreService
from pkg.response import validate_error_json, success_json, success_message
from injector import inject
from dataclasses import dataclass
from uuid import UUID
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.output_parsers.string import StrOutputParser
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.memory import BaseMemory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableConfig
from operator import itemgetter
from langchain_core.tracers.schemas import Run


@inject
@dataclass
class AppHandler:
    app_service: AppService
    vector_store_service: VectorStoreService

    def ping(self):
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

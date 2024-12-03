"""
@Time   : 2024/12/1 05:28
@Author : Leslie
@File   : app_handler.py
"""

from flask import request
import os
from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import validate_error_json, success_json, success_message
from injector import inject
from dataclasses import dataclass
from uuid import UUID
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.output_parsers.string import StrOutputParser


@inject
@dataclass
class AppHandler:
    app_service: AppService

    def ping(self):
        raise FailException(message="异常")

    def debug(self, app_id: UUID):
        """聊天接口"""
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)
        query = request.json.get("query")

        # 构建 prompt
        prompt = ChatPromptTemplate.from_template("{query}")

        # 构建 Moonshot AI 客户端
        client = MoonshotChat(
            moonshot_api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_URL"),
        )

        # 构建解析器
        str_parser = StrOutputParser()

        # 构建链
        chain = prompt | client | str_parser

        # 获取 AI 完成的内容
        content = chain.invoke({"query": query})

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

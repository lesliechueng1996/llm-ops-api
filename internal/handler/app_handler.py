"""
@Time   : 2024/12/1 05:28
@Author : Leslie
@File   : app_handler.py
"""

from flask import request
from openai import OpenAI
import os

from internal.exception import FailException
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import validate_error_json, success_json, success_message
from injector import inject
from dataclasses import dataclass
from uuid import UUID


@inject
@dataclass
class AppHandler:
    app_service: AppService

    def ping(self):
        raise FailException(message="异常")

    def completion(self):
        """聊天接口"""
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)
        query = request.json.get("query")

        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_URL"),
        )

        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {
                    "role": "system",
                    "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手, 请根据用户的输入回复对应的信息",
                },
                {"role": "user", "content": query},
            ],
        )
        content = completion.choices[0].message.content
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

"""
@Time   : 2024/12/1 05:28
@Author : Leslie
@File   : app_handler.py
"""
from flask import request
from openai import OpenAI
import os

from internal.schema.app_schema import CompletionReq
from pkg.response import validate_error_json, success_json


class AppHandler:
    def ping(self):
        return {"ping": "pong"}

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
                {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手, 请根据用户的输入回复对应的信息"},
                {"role": "user", "content": query}
            ]
        )
        content = completion.choices[0].message.content
        return success_json({"content": content})

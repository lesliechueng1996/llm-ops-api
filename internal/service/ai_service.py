"""
@Time   : 2024/12/31 20:02
@Author : Leslie
@File   : ai_service.py
"""

import json
from os import getenv
from injector import inject
from dataclasses import dataclass
from internal.entity.ai_entity import OPTIMIZE_PROMPT_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from internal.exception import NotFoundException
from internal.model.account import Account
from internal.model.conversation import Message
from internal.service.conversation_service import ConversationService
from pkg.sqlalchemy.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AIService:
    db: SQLAlchemy
    conversation_service: ConversationService

    def optimize_prompt(self, prompt: str):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", OPTIMIZE_PROMPT_TEMPLATE), ("human", "{prompt}")]
        )

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=getenv("OPENAI_KEY"),
            base_url=getenv("OPENAI_API_URL"),
            temperature=0.5,
        )

        chain = prompt_template | llm | StrOutputParser()

        for optimize_prompt in chain.stream({"prompt": prompt}):
            data = {"optimize_prompt": optimize_prompt}
            yield f"event: optimize_prompt\ndata: {json.dumps(data)}\n\n"

    def generate_suggested_questions(self, message_id: str, account: Account):
        message = (
            self.db.session.query(Message)
            .filter(Message.id == message_id, Message.created_by == account.id)
            .one_or_none()
        )
        if not message:
            raise NotFoundException("该条消息不存在或无权限")

        histories = f"Human: {message.query}\nAI: {message.answer}"

        return self.conversation_service.generate_suggested_questions(histories)

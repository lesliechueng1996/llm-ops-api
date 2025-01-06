"""
@Time   : 2024/12/23 17:20
@Author : Leslie
@File   : conversation_service.py
"""

import logging
from typing import Any
from uuid import UUID
from flask import Flask
from injector import inject
from dataclasses import dataclass
from internal.core.agent.entities.queue_entity import AgentThought, QueueEvent
from internal.entity import (
    SUMMARIZER_TEMPLATE,
    CONVERSATION_NAME_TEMPLATE,
    ConversationInfo,
    SUGGESTED_QUESTIONS_TEMPLATE,
    SuggestedQuestions,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from os import getenv
from langchain_core.output_parsers import StrOutputParser

from internal.entity.conversation_entity import InvokeFrom, MessageStatus
from internal.model.conversation import Conversation, Message, MessageAgentThought
from pkg.sqlalchemy.sqlalchemy import SQLAlchemy


@inject
@dataclass
class ConversationService:
    db: SQLAlchemy

    def summary(
        self, human_message: str, ai_message: str, old_summary: str = ""
    ) -> str:
        prompt = ChatPromptTemplate.from_template(SUMMARIZER_TEMPLATE)

        llm = ChatOpenAI(
            api_key=getenv("OPENAI_KEY"),
            base_url=getenv("OPENAI_API_URL"),
            model="gpt-4o-mini",
            temperature=0.5,
        )

        summary_chain = prompt | llm | StrOutputParser()

        new_summary = summary_chain.invoke(
            {
                "summary": old_summary,
                "new_lines": f"Human: {human_message}\nAI: {ai_message}",
            }
        )

        return new_summary

    def generate_conversation_name(self, query: str) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CONVERSATION_NAME_TEMPLATE),
                ("human", "{query}"),
            ]
        )

        llm = ChatOpenAI(
            api_key=getenv("OPENAI_KEY"),
            base_url=getenv("OPENAI_API_URL"),
            model="gpt-4o-mini",
            temperature=0,
        ).with_structured_output(ConversationInfo)

        chain = prompt | llm

        if len(query) > 2000:
            query = f"{query[:300]}...[TRUNCATED]...{query[-300:]}"
        query = query.replace("\n", " ")

        conversation_info = chain.invoke({"query": query})

        name = "新的会话"
        try:
            if conversation_info and hasattr(conversation_info, "subject"):
                name = conversation_info.subject
        except Exception as e:
            logging.exception(
                f"提取会话名称出错, conversation_info: {conversation_info}, 错误信息: {str(e)}"
            )

        if len(name) > 75:
            name = f"{name[:75]}..."

        return name

    def generate_suggested_questions(self, histories: str) -> list[str]:
        prompt = ChatPromptTemplate.from_messages(
            [("system", SUGGESTED_QUESTIONS_TEMPLATE), ("human", "{histories}")]
        )

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=getenv("OPENAI_KEY"),
            base_url=getenv("OPENAI_API_URL"),
            temperature=0,
        ).with_structured_output(SuggestedQuestions)

        chain = prompt | llm

        suggestions = chain.invoke({"histories": histories})

        questions = []

        try:
            if suggestions and hasattr(suggestions, "questions"):
                questions = suggestions.questions
        except Exception as e:
            logging.exception(
                f"提取建议问题列表出错, suggestions: {suggestions}, 错误信息: {str(e)}"
            )
        if len(questions) > 3:
            questions = questions[:3]

        return questions

    def save_agent_thoughts(
        self,
        flask_app: Flask,
        account_id: UUID,
        app_id: UUID,
        app_config: dict,
        conversation_id: UUID,
        message_id: UUID,
        agent_thoughts: list[AgentThought],
    ):
        with flask_app.app_context():
            position = 0
            latency = 0

            conversation = (
                self.db.session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .one_or_none()
            )
            message = (
                self.db.session.query(Message)
                .filter(Message.id == message_id)
                .one_or_none()
            )

            for agent_thought in agent_thoughts:
                if agent_thought.event in [
                    QueueEvent.LONG_TERM_MEMORY_RECALL,
                    QueueEvent.AGENT_THOUGHT,
                    QueueEvent.AGENT_MESSAGE,
                    QueueEvent.AGENT_ACTION,
                    QueueEvent.DATASET_RETRIEVAL,
                ]:
                    position += 1
                    latency += agent_thought.latency

                    with self.db.auto_commit():
                        message_agent_thought = MessageAgentThought(
                            app_id=app_id,
                            conversation_id=conversation_id,
                            message_id=message.id,
                            invoke_from=InvokeFrom.DEBUGGER,
                            created_by=account_id,
                            position=position,
                            event=agent_thought.event,
                            thought=agent_thought.thought,
                            observation=agent_thought.observation,
                            tool=agent_thought.tool,
                            tool_input=agent_thought.tool_input,
                            message=agent_thought.message,
                            answer=agent_thought.answer,
                            latency=agent_thought.latency,
                        )
                        self.db.session.add(message_agent_thought)

                if agent_thought.event == QueueEvent.AGENT_MESSAGE:
                    with self.db.auto_commit():
                        message.message = agent_thought.message
                        message.answer = agent_thought.answer
                        message.latency = latency

                    if app_config["long_term_memory"]["enable"]:
                        new_summary = self.summary(
                            message.query,
                            agent_thought.answer,
                            conversation.summary,
                        )

                        with self.db.auto_commit():
                            conversation.summary = new_summary

                    if conversation.is_new:
                        new_conversation_name = self.generate_conversation_name(
                            message.query
                        )
                        with self.db.auto_commit():
                            conversation.name = new_conversation_name

                if agent_thought.event in [
                    QueueEvent.STOP,
                    QueueEvent.ERROR,
                    QueueEvent.TIMEOUT,
                ]:
                    with self.db.auto_commit():
                        message.status = agent_thought.event
                        message.observation = agent_thought.observation
                    break

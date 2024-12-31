"""
@Time   : 2024/12/23 17:20
@Author : Leslie
@File   : conversation_service.py
"""

import logging
from injector import inject
from dataclasses import dataclass
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


@inject
@dataclass
class ConversationService:

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

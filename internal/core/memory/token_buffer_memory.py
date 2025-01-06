"""
@Time   : 2024/12/23 20:46
@Author : Leslie
@File   : token_buffer_memory.py
"""

from dataclasses import dataclass
from internal.model import Conversation, Message
from pkg.sqlalchemy import SQLAlchemy
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import (
    AnyMessage,
    trim_messages,
    HumanMessage,
    AIMessage,
    get_buffer_string,
)
from internal.entity import MessageStatus
from sqlalchemy import desc


@dataclass
class TokenBufferMemory:
    conversation: Conversation
    db: SQLAlchemy
    model_instance: BaseLanguageModel

    def get_history_prompt_messages(
        self, max_token_limit: int = 200, max_message_limit: int = 10
    ) -> list[AnyMessage]:
        if self.conversation is None:
            return []

        messages = (
            self.db.session.query(Message)
            .filter(
                Message.conversation_id == self.conversation.id,
                Message.answer != "",
                Message.is_deleted == False,
                Message.status.in_(
                    [MessageStatus.NORMAL, MessageStatus.STOP, MessageStatus.TIMEOUT]
                ),
            )
            .order_by(desc("created_at"))
            .limit(max_message_limit)
            .all()
        )
        messages = list(reversed(messages))

        prompt_messages = []
        for message in messages:
            prompt_messages.extend(
                [
                    HumanMessage(content=message.query),
                    AIMessage(content=message.answer),
                ]
            )

        return trim_messages(
            messages=prompt_messages,
            max_tokens=max_token_limit,
            token_counter=self.model_instance,
            strategy="last",
            start_on="human",
            end_on="ai",
        )

    def get_history_prompt_text(
        self,
        max_token_limit: int = 2000,
        max_message_limit: int = 10,
        human_prefix: str = "Human: ",
        ai_prefix: str = "AI: ",
    ) -> str:
        messages = self.get_history_prompt_messages(
            max_token_limit=max_token_limit, max_message_limit=max_message_limit
        )

        return get_buffer_string(
            messages, human_prefix=human_prefix, ai_prefix=ai_prefix
        )

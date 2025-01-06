"""
@Time   : 2025/01/06 22:53
@Author : Leslie
@File   : openapi_service.py
"""

from dataclasses import dataclass
import json
from os import getenv
from threading import Thread
from typing import Generator

from flask import current_app
from injector import inject
from internal.core.agent.agents.function_call_agent import FunctionCallAgent
from internal.core.agent.entities.agent_entity import AgentConfig
from internal.core.agent.entities.queue_entity import QueueEvent
from internal.core.memory.token_buffer_memory import TokenBufferMemory
from internal.entity.app_entity import AppStatus
from internal.entity.conversation_entity import InvokeFrom, MessageStatus
from internal.entity.dataset_entity import RetrievalSource
from internal.model.account import Account
from internal.model.api_key import EndUser
from internal.model.conversation import Conversation, Message
from internal.schema.openapi_schema import OpenapiChatReqSchema
from internal.service.app_config_serice import AppConfigService
from internal.service.app_service import AppService
from internal.exception import NotFoundException
from internal.service.conversation_service import ConversationService
from internal.service.retrieval_service import RetrievalService
from pkg.response.response import Response
from pkg.sqlalchemy import SQLAlchemy
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from internal.lib.helper import datetime_to_timestamp


@inject
@dataclass
class OpenapiService:
    app_service: AppService
    db: SQLAlchemy
    app_config_service: AppConfigService
    retrieval_service: RetrievalService
    conversation_service: ConversationService

    def chat(self, req: OpenapiChatReqSchema, account: Account):
        app = self.app_service.get_and_validate_app(req.app_id.data, account)

        if app.status != AppStatus.PUBLISHED:
            raise NotFoundException("应用未发布")

        if req.end_user_id.data:
            end_user = (
                self.db.session.query(EndUser)
                .filter(EndUser.id == req.end_user_id.data)
                .one_or_none()
            )
            if not end_user or end_user.app_id != app.id:
                raise NotFoundException("终端用户不存在，或者不属于该应用")
        else:
            end_user = EndUser(
                tenant_id=account.id,
                app_id=app.id,
            )
            self.db.session.add(end_user)
            self.db.session.commit()

        if req.conversation_id.data:
            conversation = (
                self.db.session.query(Conversation)
                .filter(Conversation.id == req.conversation_id.data)
                .one_or_none()
            )
            if (
                not conversation
                or conversation.app_id != app.id
                or conversation.invoke_from != InvokeFrom.SERVICE_API
                or conversation.created_by != end_user.id
            ):
                raise NotFoundException(
                    "会话不存在，或者不属于该应用/终端用户/调用来源"
                )
        else:
            conversation = Conversation(
                app_id=app.id,
                name="New Conversation",
                invoke_from=InvokeFrom.SERVICE_API,
                created_by=end_user.id,
            )
            self.db.session.add(conversation)
            self.db.session.commit()

        app_config = self.app_config_service.get_app_config(app)

        message = Message(
            app_id=app.id,
            conversation_id=conversation.id,
            invoke_from=InvokeFrom.SERVICE_API,
            created_by=end_user.id,
            query=req.query.data,
            status=MessageStatus.NORMAL,
        )
        self.db.session.add(message)
        self.db.session.commit()

        # TODO 创建 LLM
        llm = ChatOpenAI(
            model=app_config["model_config"]["model"],
            **app_config["model_config"]["parameters"],
            api_key=getenv("OPENAI_KEY"),
            base_url=getenv("OPENAI_API_URL"),
        )

        token_buffer_memory = TokenBufferMemory(
            conversation=conversation,
            db=self.db,
            model_instance=llm,
        )
        history = token_buffer_memory.get_history_prompt_messages(
            max_message_limit=app_config["dialog_round"],
        )

        tools = self.app_config_service.get_langchain_tools_by_tool_config(
            app_config["tools"],
            account=account,
        )

        if app_config["datasets"]:
            dataset_retrieval = (
                self.retrieval_service.create_langchain_tool_from_search(
                    flask_app=current_app._get_current_object(),
                    account_id=account.id,
                    dataset_ids=[dataset["id"] for dataset in app_config["datasets"]],
                    retrival_source=RetrievalSource.APP,
                    **app_config["retrieval_config"],
                )
            )
            tools.append(dataset_retrieval)

        agent = FunctionCallAgent(
            llm=llm,
            agent_config=AgentConfig(
                user_id=account.id,
                invoke_from=InvokeFrom.SERVICE_API,
                review_config=app_config["review_config"],
                enable_long_term_memory=app_config["long_term_memory"]["enable"],
                tools=tools,
            ),
        )

        agent_state = {
            "messages": [HumanMessage(req.query.data)],
            "history": history,
            "long_term_memory": conversation.summary,
        }

        if req.stream.data:
            agent_thoughts_dict = {}

            def handle_stream() -> Generator:
                for agent_thought in agent.stream(agent_state):
                    event_id = str(agent_thought.id)

                    if agent_thought.event != QueueEvent.PING:
                        if agent_thought.event == QueueEvent.AGENT_MESSAGE:
                            if event_id not in agent_thoughts_dict:
                                agent_thoughts_dict[event_id] = agent_thought
                            else:
                                agent_thoughts_dict[event_id] = agent_thoughts_dict[
                                    event_id
                                ].model_copy(
                                    update={
                                        "thought": f"{agent_thoughts_dict[event_id].thought}{agent_thought.thought}",
                                        "answer": f"{agent_thoughts_dict[event_id].answer}{agent_thought.answer}",
                                        "latency": agent_thought.latency,
                                    }
                                )
                        else:
                            agent_thoughts_dict[event_id] = agent_thought

                    data = {
                        **agent_thought.model_dump(
                            include={
                                "event",
                                "thought",
                                "observation",
                                "tool",
                                "tool_input",
                                "answer",
                                "latency",
                            }
                        ),
                        "id": event_id,
                        "end_user_id": str(end_user.id),
                        "conversation_id": str(conversation.id),
                        "message_id": str(message.id),
                        "task_id": str(agent_thought.task_id),
                    }

                    yield f"event: {agent_thought.event}\ndata: {json.dumps(data)}\n\n"

                thread = Thread(
                    target=self.conversation_service.save_agent_thoughts,
                    kwargs={
                        "flask_app": current_app._get_current_object(),
                        "account_id": account.id,
                        "app_id": app.id,
                        "app_config": app_config,
                        "conversation_id": conversation.id,
                        "message_id": message.id,
                        "agent_thoughts": [
                            agent_thought
                            for agent_thought in agent_thoughts_dict.values()
                        ],
                    },
                )
                thread.start()

            return handle_stream()

        agent_result = agent.invoke(agent_state)

        thread = Thread(
            target=self.conversation_service.save_agent_thoughts,
            kwargs={
                "flask_app": current_app._get_current_object(),
                "account_id": account.id,
                "app_id": app.id,
                "app_config": app_config,
                "conversation_id": conversation.id,
                "message_id": message.id,
                "agent_thoughts": agent_result.agent_thoughts,
            },
        )
        thread.start()

        return Response(
            data={
                "id": str(message.id),
                "end_user_id": str(end_user.id),
                "conversation_id": str(conversation.id),
                "query": req.query.data,
                "answer": agent_result.answer,
                "total_token_count": agent_result.total_token_count,
                "latency": agent_result.latency,
                "agent_thoughts": [
                    {
                        "id": str(agent_thought.id),
                        "event": agent_thought.event,
                        "thought": agent_thought.thought,
                        "observation": agent_thought.observation,
                        "tool": agent_thought.tool,
                        "tool_input": agent_thought.tool_input,
                        "latency": agent_thought.latency,
                        "created_at": 0,
                    }
                    for agent_thought in agent_result.agent_thoughts
                ],
                "created_at": datetime_to_timestamp(message.created_at),
            }
        )

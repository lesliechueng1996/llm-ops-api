"""
@Time   : 2024/12/02 01:53
@Author : Leslie
@File   : app_service.py
"""

from datetime import datetime
import json
from os import getenv
from threading import Thread
from typing import Any
from redis import Redis
from internal.core.agent.agents.agent_queue_manager import AgentQueueManager
from internal.core.agent.entities.queue_entity import QueueEvent
from internal.model import Account, ApiTool, Dataset, AppConfig
from internal.model.conversation import Conversation, Message, MessageAgentThought
from internal.schema.app_schema import (
    CreateAppReqSchema,
    GetAppDebugSummaryReqSchema,
    GetConversationMessagesReqSchema,
    UpdateAppReqSchema,
)
from internal.service.app_config_serice import AppConfigService
from internal.service.conversation_service import ConversationService
from pkg.sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from injector import inject
from internal.model.app import App, AppConfigVersion, AppDatasetJoin
from uuid import UUID
from internal.entity.app_entity import AppStatus, AppConfigType, DEFAULT_APP_CONFIG
from internal.exception import NotFoundException, ValidateErrorException, FailException
from internal.core.tools.builtin_tools.providers import BuiltinProviderManager
from internal.lib.helper import datetime_to_timestamp
from sqlalchemy import asc, desc, func
from pkg.pagination import PaginationReq, Paginator
from internal.entity.conversation_entity import InvokeFrom, MessageStatus
from langchain_openai import ChatOpenAI
from internal.core.memory import TokenBufferMemory
from .retrieval_service import RetrievalService
from flask import current_app
from internal.entity import RetrievalSource
from internal.core.agent.agents.function_call_agent import FunctionCallAgent
from internal.core.agent.entities.agent_entity import AgentConfig
from langchain_core.messages import HumanMessage


@inject
@dataclass
class AppService:
    db: SQLAlchemy
    builtin_provider_manager: BuiltinProviderManager
    retrieval_service: RetrievalService
    redis_client: Redis
    conversation_service: ConversationService
    app_config_service: AppConfigService

    def debug_chat(self, app_id: UUID, query: str, account: Account):
        app = self._get_app(app_id, account)

        draft_app_config = self.get_draft_app_config(app_id, account)

        debug_conversation = self._get_debug_conversation_or_create(app, account)

        with self.db.auto_commit():
            message = Message(
                app_id=app_id,
                conversation_id=debug_conversation.id,
                invoke_from=InvokeFrom.DEBUGGER,
                created_by=account.id,
                query=query,
                status=MessageStatus.NORMAL,
            )
            self.db.session.add(message)

        llm = ChatOpenAI(
            model=draft_app_config["model_config"]["model"],
            **draft_app_config["model_config"]["parameters"],
            api_key=getenv("OPENAI_KEY"),
            base_url=getenv("OPENAI_API_URL"),
        )

        token_buffer_memory = TokenBufferMemory(
            conversation=debug_conversation,
            db=self.db,
            model_instance=llm,
        )
        history = token_buffer_memory.get_history_prompt_messages(
            max_message_limit=draft_app_config["dialog_round"],
        )

        tools = self.app_config_service.get_langchain_tools_by_tool_config(
            draft_app_config["tools"],
            account=account,
        )

        if draft_app_config["datasets"]:
            dataset_retrieval = (
                self.retrieval_service.create_langchain_tool_from_search(
                    flask_app=current_app._get_current_object(),
                    account_id=account.id,
                    dataset_ids=[
                        dataset["id"] for dataset in draft_app_config["datasets"]
                    ],
                    retrival_source=RetrievalSource.APP,
                    **draft_app_config["retrieval_config"],
                )
            )
            tools.append(dataset_retrieval)

        agent = FunctionCallAgent(
            llm=llm,
            agent_config=AgentConfig(
                user_id=account.id,
                invoke_from=InvokeFrom.DEBUGGER,
                review_config=draft_app_config["review_config"],
                enable_long_term_memory=draft_app_config["long_term_memory"]["enable"],
                tools=tools,
            ),
        )

        agent_thoughts = {}
        response = agent.stream(
            {
                "messages": [HumanMessage(query)],
                "history": history,
                "long_term_memory": debug_conversation.summary,
            }
        )
        for agent_thought in response:
            event_id = str(agent_thought.id)

            if agent_thought.event != QueueEvent.PING:
                if agent_thought.event == QueueEvent.AGENT_MESSAGE:
                    if event_id not in agent_thoughts:
                        agent_thoughts[event_id] = agent_thought
                    else:
                        agent_thoughts[event_id] = agent_thoughts[event_id].model_copy(
                            update={
                                "thought": f"{agent_thoughts[event_id].thought}{agent_thought.thought}",
                                "answer": f"{agent_thoughts[event_id].answer}{agent_thought.answer}",
                                "latency": agent_thought.latency,
                            }
                        )
                else:
                    agent_thoughts[event_id] = agent_thought

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
                "conversation_id": str(debug_conversation.id),
                "message_id": str(message.id),
                "task_id": str(agent_thought.task_id),
            }

            yield f"event: {agent_thought.event}\ndata: {json.dumps(data)}\n\n"

        thread = Thread(
            target=self.conversation_service.save_agent_thoughts,
            kwargs={
                "flask_app": current_app._get_current_object(),
                "account_id": account.id,
                "app_id": app_id,
                "app_config": draft_app_config,
                "conversation_id": debug_conversation.id,
                "message_id": message.id,
                "agent_thoughts": [
                    agent_thought for agent_thought in agent_thoughts.values()
                ],
            },
        )
        thread.start()

    def create_app(self, req: CreateAppReqSchema, account: Account) -> App:
        with self.db.auto_commit():
            app = App(
                account_id=account.id,
                name=req.name.data,
                description=req.description.data or "",
                icon=req.icon.data,
                status=AppStatus.DRAFT,
            )
            self.db.session.add(app)
            self.db.session.flush()

            app_config_version = AppConfigVersion(
                app_id=app.id,
                version=0,
                config_type=AppConfigType.DRAFT,
                **DEFAULT_APP_CONFIG,
            )
            self.db.session.add(app_config_version)
            self.db.session.flush()

            app.draft_app_config_id = app_config_version.id
        return app

    def get_app(self, id: UUID, account: Account):
        app = (
            self.db.session.query(App)
            .filter(App.id == id, App.account_id == account.id)
            .one_or_none()
        )

        if not app:
            raise NotFoundException("应用不存在")

        draft_app_config_id = app.draft_app_config_id
        app_config_version = (
            self.db.session.query(AppConfigVersion)
            .filter(
                AppConfigVersion.id == draft_app_config_id,
                AppConfigVersion.config_type == AppConfigType.DRAFT,
            )
            .one_or_none()
        )

        if app_config_version is None:
            with self.db.auto_commit():
                app_config_version = AppConfigVersion(
                    app_id=app.id,
                    version=0,
                    config_type=AppConfigType.DRAFT,
                    **DEFAULT_APP_CONFIG,
                )
                self.db.session.add(app_config_version)
                self.db.session.flush()
                app.draft_app_config_id = app_config_version.id
        return {
            "app": app,
            "draft_updated_at": app_config_version.updated_at,
        }

    def update_app(self, id: UUID, account: Account, req: UpdateAppReqSchema):
        with self.db.auto_commit():
            app = self._get_app(id, account)
            app.name = req.name.data
            app.icon = req.icon.data
            app.description = req.description.data or ""

    def delete_app(self, id: UUID, account: Account):
        with self.db.auto_commit():
            app = self._get_app(id, account)
            self.db.session.delete(app)

    def get_publish_histories(self, app_id: UUID, req: PaginationReq, account: Account):
        self._get_app(app_id, account)

        paginator = Paginator(self.db, req)

        data = paginator.paginate(
            self.db.session.query(AppConfigVersion)
            .filter(
                AppConfigVersion.app_id == app_id,
                AppConfigVersion.config_type == AppConfigType.PUBLISHED,
            )
            .order_by(desc("version"))
        )

        return data, paginator

    def cancel_publish(self, app_id: UUID, account: Account):
        app = self._get_app(app_id, account)

        if app.status != AppStatus.PUBLISHED:
            raise FailException("应用未发布")

        with self.db.auto_commit():
            app.status = AppStatus.DRAFT
            app.app_config_id = None

            self.db.session.query(AppDatasetJoin).filter(
                AppDatasetJoin.app_id == app.id
            ).delete()

        return app

    def fallback_history(
        self, app_id: UUID, app_config_version_id: str, account: Account
    ):
        app = self._get_app(app_id, account)

        app_config_version = (
            self.db.session.query(AppConfigVersion)
            .filter(
                AppConfigVersion.id == app_config_version_id,
                AppConfigVersion.app_id == app_id,
                AppConfigVersion.config_type == AppConfigType.PUBLISHED,
            )
            .one_or_none()
        )

        if not app_config_version:
            raise NotFoundException("应用配置不存在")

        draft_app_config_dict = app_config_version.__dict__.copy()
        remove_fields = [
            "id",
            "app_id",
            "version",
            "config_type",
            "created_at",
            "updated_at",
            "_sa_instance_state",
        ]
        for field in remove_fields:
            draft_app_config_dict.pop(field)

        draft_app_config_dict = self._validate_draft_app_config(
            draft_app_config_dict, account
        )

        current_draft_app_config = (
            self.db.session.query(AppConfigVersion)
            .filter(AppConfigVersion.id == app.draft_app_config_id)
            .one_or_none()
        )

        with self.db.auto_commit():
            for key, value in draft_app_config_dict.items():
                setattr(current_draft_app_config, key, value)
            current_draft_app_config.updated_at = datetime.now()

    def get_app_debug_summary(self, app_id: UUID, account: Account):
        app = self._get_app(app_id, account)

        current_draft_app_config = (
            self.db.session.query(AppConfigVersion)
            .filter(
                AppConfigVersion.id == app.draft_app_config_id,
                AppConfigVersion.config_type == AppConfigType.DRAFT,
            )
            .one_or_none()
        )
        if not current_draft_app_config:
            raise NotFoundException("应用配置不存在")

        if current_draft_app_config.long_term_memory["enable"] is False:
            raise FailException("长期记忆未启用")

        debug_conversation_id = app.debug_conversation_id
        conversation = (
            self.db.session.query(Conversation)
            .filter(
                Conversation.id == debug_conversation_id,
                Conversation.app_id == app.id,
            )
            .one_or_none()
        )
        if conversation is None:
            with self.db.auto_commit():
                conversation = Conversation(
                    app_id=app.id,
                    name="New Conversation",
                    invoke_from=InvokeFrom.DEBUGGER,
                    created_by=account.id,
                )
                self.db.session.add(conversation)
                self.db.session.flush()

                app.debug_conversation_id = conversation.id

        return conversation.summary

    def update_app_debug_summary(self, app_id: UUID, summary: str, account: Account):
        app = self._get_app(app_id, account)

        current_draft_app_config = (
            self.db.session.query(AppConfigVersion)
            .filter(
                AppConfigVersion.id == app.draft_app_config_id,
                AppConfigVersion.config_type == AppConfigType.DRAFT,
            )
            .one_or_none()
        )
        if not current_draft_app_config:
            raise NotFoundException("应用配置不存在")

        if current_draft_app_config.long_term_memory["enable"] is False:
            raise FailException("长期记忆未启用")

        debug_conversation_id = app.debug_conversation_id
        conversation = (
            self.db.session.query(Conversation)
            .filter(
                Conversation.id == debug_conversation_id,
                Conversation.app_id == app.id,
            )
            .one_or_none()
        )
        if conversation is None:
            with self.db.auto_commit():
                conversation = Conversation(
                    app_id=app.id,
                    name="New Conversation",
                    invoke_from=InvokeFrom.DEBUGGER,
                    created_by=account.id,
                    summary=summary,
                )
                self.db.session.add(conversation)
                self.db.session.flush()

                app.debug_conversation_id = conversation.id

        with self.db.auto_commit():
            conversation.summary = summary

    def delete_app_debug_conversations(self, app_id: UUID, account: Account):
        app = self._get_app(app_id, account)

        if not app.debug_conversation_id:
            return

        with self.db.auto_commit():
            app.debug_conversation_id = None

    def get_draft_app_config(self, app_id: UUID, account: Account):
        app = self._get_app(app_id, account)
        return self.app_config_service.get_draft_app_config(app)

    def update_draft_app_config(
        self, app_id: UUID, draft_app_config: dict[str, Any], account: Account
    ) -> AppConfigVersion:
        app = self._get_app(app_id, account)

        draft_app_config = self._validate_draft_app_config(draft_app_config, account)

        app_config_version = (
            self.db.session.query(AppConfigVersion)
            .filter(
                AppConfigVersion.id == app.draft_app_config_id,
                AppConfigVersion.config_type == AppConfigType.DRAFT,
            )
            .one_or_none()
        )

        with self.db.auto_commit():
            for key, value in draft_app_config.items():
                setattr(app_config_version, key, value)

        return app_config_version

    def publish_app_config(self, app_id: UUID, account: Account):
        app = self._get_app(app_id, account)

        draft_app_config_dict = self.get_draft_app_config(app_id, account)

        with self.db.auto_commit():
            app_config = AppConfig(
                app_id=app.id,
                model_config=draft_app_config_dict["model_config"],
                dialog_round=draft_app_config_dict["dialog_round"],
                preset_prompt=draft_app_config_dict["preset_prompt"],
                tools=[
                    {
                        "type": tool["type"],
                        "provider_id": tool["provider"]["id"],
                        "tool_id": tool["tool"]["id"],
                        "params": tool["tool"]["params"],
                    }
                    for tool in draft_app_config_dict["tools"]
                ],
                workflows=draft_app_config_dict["workflows"],
                retrieval_config=draft_app_config_dict["retrieval_config"],
                long_term_memory=draft_app_config_dict["long_term_memory"],
                opening_statement=draft_app_config_dict["opening_statement"],
                opening_questions=draft_app_config_dict["opening_questions"],
                speech_to_text=draft_app_config_dict["speech_to_text"],
                text_to_speech=draft_app_config_dict["text_to_speech"],
                suggested_after_answer=draft_app_config_dict["suggested_after_answer"],
                review_config=draft_app_config_dict["review_config"],
            )
            self.db.session.add(app_config)
            self.db.session.flush()

            app.app_config_id = app_config.id
            app.status = AppStatus.PUBLISHED

            self.db.session.query(AppDatasetJoin).filter(
                AppDatasetJoin.app_id == app.id
            ).delete()

            for dataset in draft_app_config_dict["datasets"]:
                self.db.session.add(
                    AppDatasetJoin(app_id=app.id, dataset_id=dataset["id"])
                )

            draft_app_config = (
                self.db.session.query(AppConfigVersion)
                .filter(AppConfigVersion.id == app.draft_app_config_id)
                .one_or_none()
            )

            draft_app_config_copy = draft_app_config.__dict__.copy()
            remove_fields = [
                "id",
                "version",
                "config_type",
                "created_at",
                "updated_at",
                "_sa_instance_state",
            ]
            for field in remove_fields:
                draft_app_config_copy.pop(field)

            max_version = (
                self.db.session.query(
                    func.coalesce(func.max(AppConfigVersion.version), 0)
                )
                .filter(
                    AppConfigVersion.app_id == app.id,
                    AppConfigVersion.config_type == AppConfigType.PUBLISHED,
                )
                .scalar()
            )

            app_config_version = AppConfigVersion(
                **draft_app_config_copy,
                version=max_version + 1,
                config_type=AppConfigType.PUBLISHED,
            )
            self.db.session.add(app_config_version)
        return app

    def _validate_draft_app_config(
        self, draft_app_config: dict[str, Any], account: Account
    ) -> dict[str, Any]:
        # 校验字段
        acceptable_fields = [
            "model_config",
            "dialog_round",
            "preset_prompt",
            "tools",
            "workflows",
            "datasets",
            "retrieval_config",
            "long_term_memory",
            "opening_statement",
            "opening_questions",
            "speech_to_text",
            "text_to_speech",
            "review_config",
            "suggested_after_answer",
        ]

        if (
            not draft_app_config
            or not isinstance(draft_app_config, dict)
            or set(draft_app_config.keys()) - set(acceptable_fields)
        ):
            raise ValidateErrorException(
                "配置格式错误：请确保包含且仅包含有效的配置字段"
            )

        # TODO 校验 model_config

        # 校验 dialog_round
        if "dialog_round" in draft_app_config:
            dialog_round = draft_app_config["dialog_round"]
            if not isinstance(dialog_round, int) or not (0 <= dialog_round <= 100):
                raise ValidateErrorException("对话轮次设置无效：请输入0-100之间的整数")

        # 校验 preset_prompt
        if "preset_prompt" in draft_app_config:
            preset_prompt = draft_app_config["preset_prompt"]
            if not isinstance(preset_prompt, str) or len(preset_prompt) > 2000:
                raise ValidateErrorException(
                    "人设与回复逻辑设置无效：内容不能超过2000字符"
                )

        # 校验 tools
        if "tools" in draft_app_config:
            tools = draft_app_config["tools"]
            validate_tools = []

            if not isinstance(tools, list):
                raise ValidateErrorException("插件配置格式错误：必须为数组格式")
            if len(tools) > 5:
                raise ValidateErrorException("插件数量超限：最多支持5个插件")

            for tool in tools:
                if not tool or not isinstance(tool, dict):
                    raise ValidateErrorException(
                        "插件配置格式错误：每个插件必须包含完整配置信息"
                    )
                if set(tool.keys()) != {"type", "provider_id", "tool_id", "params"}:
                    raise ValidateErrorException(
                        "插件配置缺失：必须包含类型、提供者ID、工具ID和参数信息"
                    )
                if tool["type"] not in ["builtin_tool", "api_tool"]:
                    raise ValidateErrorException(
                        "插件类型错误：仅支持内置插件或API插件"
                    )
                if not tool["provider_id"] or not isinstance(tool["provider_id"], str):
                    raise ValidateErrorException(
                        "插件提供者ID无效：必须提供有效的字符串标识"
                    )
                if not tool["tool_id"] or not isinstance(tool["tool_id"], str):
                    raise ValidateErrorException(
                        "插件工具ID无效：必须提供有效的字符串标识"
                    )
                if not isinstance(tool["params"], dict):
                    raise ValidateErrorException("插件参数格式错误：必须为对象格式")

                if tool["type"] == "builtin_tool":
                    builtin_tool = self.builtin_provider_manager.get_tool(
                        tool["provider_id"], tool["tool_id"]
                    )
                    if not builtin_tool:
                        continue
                else:
                    api_tool = (
                        self.db.session.query(ApiTool)
                        .filter(
                            ApiTool.provider_id == tool["provider_id"],
                            ApiTool.id == tool["tool_id"],
                            ApiTool.account_id == account.id,
                        )
                        .one_or_none()
                    )
                    if not api_tool:
                        continue

                validate_tools.append(tool)

            check_tools = [
                f"{tool['provider_id']}_{tool['tool_id']}" for tool in validate_tools
            ]
            if len(set(check_tools)) != len(validate_tools):
                raise ValidateErrorException("插件重复：每个插件只能添加一次")

            draft_app_config["tools"] = validate_tools

        # TODO 校验 workflows

        # 校验 datasets
        if "datasets" in draft_app_config:
            datasets = draft_app_config["datasets"]

            if not isinstance(datasets, list):
                raise ValidateErrorException("知识库配置格式错误：必须为数组格式")
            if len(datasets) > 5:
                raise ValidateErrorException("知识库数量超限：最多支持5个知识库")

            if len(set(datasets)) != len(datasets):
                raise ValidateErrorException("知识库重复：每个知识库只能添加一次")

            dataset_records = (
                self.db.session.query(Dataset)
                .filter(
                    Dataset.id.in_(datasets),
                    Dataset.account_id == account.id,
                )
                .all()
            )
            draft_app_config["datasets"] = [
                str(dataset.id) for dataset in dataset_records
            ]

        # 校验 retrieval_config
        if "retrieval_config" in draft_app_config:
            retrieval_config = draft_app_config["retrieval_config"]
            if not retrieval_config or not isinstance(retrieval_config, dict):
                raise ValidateErrorException("检索配置格式错误：必须提供完整的检索设置")

            if set(retrieval_config.keys()) != {"retrieval_strategy", "k", "score"}:
                raise ValidateErrorException(
                    "检索配置缺失：必须包含检索策略、数量限制和匹配度设置"
                )

            if retrieval_config["retrieval_strategy"] not in [
                "full_text",
                "semantic",
                "hybrid",
            ]:
                raise ValidateErrorException("检索策略无效：仅支持全文、语义或混合检索")

            if not isinstance(retrieval_config["k"], int) or not (
                0 <= retrieval_config["k"] <= 10
            ):
                raise ValidateErrorException("召回数量设置无效：请输入0-10之间的整数")

            if not isinstance(retrieval_config["score"], float) or not (
                0 <= retrieval_config["score"] <= 1
            ):
                raise ValidateErrorException("匹配度阈值无效：请输入0-1之间的小数")

        # 校验 long_term_memory
        if "long_term_memory" in draft_app_config:
            long_term_memory = draft_app_config["long_term_memory"]
            if not long_term_memory or not isinstance(long_term_memory, dict):
                raise ValidateErrorException(
                    "长期记忆配置格式错误：必须提供完整配置信息"
                )

            if set(long_term_memory.keys()) != {"enable"} or not isinstance(
                long_term_memory["enable"], bool
            ):
                raise ValidateErrorException(
                    "长期记忆配置缺失：必须包含且仅包含启用状态字段"
                )

        # 校验 opening_statement
        if "opening_statement" in draft_app_config:
            opening_statement = draft_app_config["opening_statement"]
            if not isinstance(opening_statement, str) or len(opening_statement) > 2000:
                raise ValidateErrorException(
                    "开场白设置无效：请输入不超过2000字符的文本内容"
                )

        # 校验 opening_questions
        if "opening_questions" in draft_app_config:
            opening_questions = draft_app_config["opening_questions"]
            if not isinstance(opening_questions, list):
                raise ValidateErrorException("建议问题格式错误：必须为数组格式")
            if len(opening_questions) > 3:
                raise ValidateErrorException("建议问题数量超限：最多支持3个问题")

            for question in opening_questions:
                if not isinstance(question, str):
                    raise ValidateErrorException(
                        "建议问题格式错误：每个问题必须是文本内容"
                    )

        # 校验 speech_to_text
        if "speech_to_text" in draft_app_config:
            speech_to_text = draft_app_config["speech_to_text"]
            if not speech_to_text or not isinstance(speech_to_text, dict):
                raise ValidateErrorException(
                    "语音转文本配置格式错误：必须提供完整配置信息"
                )

            if set(speech_to_text.keys()) != {"enable"} or not isinstance(
                speech_to_text["enable"], bool
            ):
                raise ValidateErrorException(
                    "语音转文本配置缺失：必须包含且仅包含启用状态字段"
                )

        # 校验 text_to_speech
        if "text_to_speech" in draft_app_config:
            text_to_speech = draft_app_config["text_to_speech"]
            if not isinstance(text_to_speech, dict):
                raise ValidateErrorException(
                    "文本转语音配置格式错误：必须提供完整配置信息"
                )

            if (
                set(text_to_speech.keys())
                != {
                    "enable",
                    "auto_play",
                    "voice",
                }
                or not isinstance(text_to_speech["enable"], bool)
                or not isinstance(text_to_speech["auto_play"], bool)
                or text_to_speech["voice"] not in ["echo"]
            ):
                raise ValidateErrorException(
                    "文本转语音配置无效：必须包含启用状态、自动播放和语音类型(仅支持echo)字段"
                )

        # 校验 suggested_after_answer
        if "suggested_after_answer" in draft_app_config:
            suggested_after_answer = draft_app_config["suggested_after_answer"]
            if not suggested_after_answer or not isinstance(
                suggested_after_answer, dict
            ):
                raise ValidateErrorException(
                    "回答后建议问题配置格式错误：必须提供完整配置信息"
                )

            if set(suggested_after_answer.keys()) != {"enable"} or not isinstance(
                suggested_after_answer["enable"], bool
            ):
                raise ValidateErrorException(
                    "回答后建议问题配置缺失：必须包含且仅包含启用状态字段"
                )

        # 校验 review_config
        if "review_config" in draft_app_config:
            review_config = draft_app_config["review_config"]
            if not review_config or not isinstance(review_config, dict):
                raise ValidateErrorException("审核配置格式错误：必须提供完整配置信息")

            if set(review_config.keys()) != {
                "enable",
                "keywords",
                "inputs_config",
                "outputs_config",
            }:
                raise ValidateErrorException(
                    "审核配置缺失：必须包含启用状态、关键词、输入配置和输出配置"
                )

            if not isinstance(review_config["enable"], bool):
                raise ValidateErrorException("审核启用状态格式错误：必须为布尔值")

            if (
                not isinstance(review_config["keywords"], list)
                or (review_config["enable"] and len(review_config["keywords"]) == 0)
                or len(review_config["keywords"]) > 100
            ):
                raise ValidateErrorException(
                    "关键词配置无效：启用审核时必须提供至少1个且不超过100个关键词"
                )

            for keyword in review_config["keywords"]:
                if not isinstance(keyword, str):
                    raise ValidateErrorException(
                        "关键词格式错误：每个关键词必须是文本内容"
                    )

            if not review_config["inputs_config"] or not isinstance(
                review_config["inputs_config"], dict
            ):
                raise ValidateErrorException(
                    "输入审核配置格式错误：必须提供完整配置信息"
                )

            if (
                set(review_config["inputs_config"].keys())
                != {
                    "enable",
                    "preset_response",
                }
                or not isinstance(review_config["inputs_config"]["enable"], bool)
                or not isinstance(
                    review_config["inputs_config"]["preset_response"], str
                )
            ):
                raise ValidateErrorException(
                    "输入审核配置缺失：必须包含启用状态和预设回复"
                )

            if not review_config["outputs_config"] or not isinstance(
                review_config["outputs_config"], dict
            ):
                raise ValidateErrorException(
                    "输出审核配置格式错误：必须提供完整配置信息"
                )

            if set(review_config["outputs_config"].keys()) != {
                "enable",
            } or not isinstance(review_config["outputs_config"]["enable"], bool):
                raise ValidateErrorException("输出审核配置缺失：必须包含启用状态字段")

            if review_config["enable"]:
                if (
                    review_config["inputs_config"]["enable"] is False
                    and review_config["outputs_config"]["enable"] is False
                ):
                    raise ValidateErrorException(
                        "审核配置无效：启用审核时必须至少启用输入审核或输出审核"
                    )

                if (
                    review_config["inputs_config"]["enable"]
                    and not review_config["inputs_config"]["preset_response"].strip()
                ):
                    raise ValidateErrorException(
                        "输入审核预设回复无效：启用输入审核时必须提供预设回复内容"
                    )

        return draft_app_config

    def get_and_validate_app(self, app_id: UUID, account: Account) -> App:
        return self._get_app(app_id, account)

    def _get_app(self, app_id: UUID, account: Account) -> App:
        app = (
            self.db.session.query(App)
            .filter(App.id == app_id, App.account_id == account.id)
            .one_or_none()
        )
        if not app:
            raise NotFoundException("应用不存在")
        return app

    def _get_debug_conversation_or_create(
        self, app: App, account: Account
    ) -> Conversation:
        debug_conversation = (
            self.db.session.query(Conversation)
            .filter(
                Conversation.id == app.debug_conversation_id,
                Conversation.app_id == app.id,
            )
            .one_or_none()
        )
        if not debug_conversation:
            with self.db.auto_commit():
                debug_conversation = Conversation(
                    app_id=app.id,
                    name="New Conversation",
                    invoke_from=InvokeFrom.DEBUGGER,
                    created_by=account.id,
                )
                self.db.session.add(debug_conversation)
                self.db.session.flush()
                app.debug_conversation_id = debug_conversation.id

        return debug_conversation

    def stop_debug_task(self, app_id: UUID, task_id: UUID, account: Account):
        self._get_app(app_id, account)

        AgentQueueManager.set_stop_flag(task_id, InvokeFrom.DEBUGGER, account.id)

    def get_conversation_messages_with_page(
        self, app_id: UUID, req: GetConversationMessagesReqSchema, account: Account
    ):
        app = self._get_app(app_id, account)

        filters = []
        if req.created_at.data:
            filters.append(
                Message.created_at <= datetime.fromtimestamp(req.created_at.data)
            )

        paginator = Paginator(self.db, req)
        messages = paginator.paginate(
            self.db.session.query(Message)
            .filter(
                Message.conversation_id == app.debug_conversation_id,
                Message.status.in_([MessageStatus.NORMAL, MessageStatus.STOP]),
                Message.answer != "",
                *filters,
            )
            .order_by(desc("created_at"))
        )

        message_ids = [message.id for message in messages]
        agent_thoughts = (
            self.db.session.query(MessageAgentThought)
            .filter(MessageAgentThought.message_id.in_(message_ids))
            .order_by(asc("position"))
            .all()
        )

        agent_thoughts_map = {}
        for agent_thought in agent_thoughts:
            if str(agent_thought.message_id) not in agent_thoughts_map:
                agent_thoughts_map[str(agent_thought.message_id)] = []
            agent_thoughts_map[str(agent_thought.message_id)].append(
                {
                    "id": str(agent_thought.id),
                    "position": agent_thought.position,
                    "event": agent_thought.event,
                    "thought": agent_thought.thought,
                    "observation": agent_thought.observation,
                    "tool": agent_thought.tool,
                    "tool_input": agent_thought.tool_input,
                    "latency": agent_thought.latency,
                    "created_at": datetime_to_timestamp(agent_thought.created_at),
                }
            )

        result = []
        for message in messages:
            result.append(
                {
                    "id": str(message.id),
                    "conversation_id": str(message.conversation_id),
                    "query": message.query,
                    "answer": message.answer,
                    "total_token_count": message.total_token_count,
                    "latency": message.latency,
                    "agent_thoughts": agent_thoughts_map.get(str(message.id), []),
                    "created_at": datetime_to_timestamp(message.created_at),
                }
            )

        return result, paginator

    def get_apps_pagination(self, req: GetAppDebugSummaryReqSchema, account: Account):
        paginator = Paginator(self.db, req)

        filters = [App.account_id == account.id]
        if req.search_word.data:
            filters.append(App.name.ilike(f"%{req.search_word.data}%"))

        data: list[App] = paginator.paginate(
            self.db.session.query(App).filter(*filters).order_by(desc("created_at"))
        )

        app_config_ids = [
            app.app_config_id
            for app in data
            if app.app_config_id and app.status == AppStatus.PUBLISHED
        ]

        draft_app_config_ids = [
            app.draft_app_config_id
            for app in data
            if app.draft_app_config_id and app.status == AppStatus.DRAFT
        ]

        app_configs = (
            self.db.session.query(AppConfig)
            .filter(AppConfig.id.in_(app_config_ids))
            .all()
        )
        app_config_map = {app_config.id: app_config for app_config in app_configs}

        draft_app_configs = (
            self.db.session.query(AppConfigVersion)
            .filter(AppConfigVersion.id.in_(draft_app_config_ids))
            .all()
        )
        draft_app_config_map = {
            draft_app_config.id: draft_app_config
            for draft_app_config in draft_app_configs
        }

        app_dict_list = [
            {
                "app": app,
                "preset_prompt": (
                    app_config_map.get(app.app_config_id).preset_prompt
                    if app.app_config_id and app.status == AppStatus.PUBLISHED
                    else draft_app_config_map.get(app.draft_app_config_id).preset_prompt
                ),
                "model": (
                    app_config_map.get(app.app_config_id).model_config["model"]
                    if app.app_config_id and app.status == AppStatus.PUBLISHED
                    else draft_app_config_map.get(app.draft_app_config_id).model_config[
                        "model"
                    ]
                ),
                "provider": (
                    app_config_map.get(app.app_config_id).model_config["provider"]
                    if app.app_config_id and app.status == AppStatus.PUBLISHED
                    else draft_app_config_map.get(app.draft_app_config_id).model_config[
                        "provider"
                    ]
                ),
            }
            for app in data
        ]

        return app_dict_list, paginator

    def copy_app(self, app_id: UUID, account: Account):
        app = self._get_app(app_id, account)

        draft_config = (
            self.db.session.query(AppConfigVersion)
            .filter(AppConfigVersion.id == app.draft_app_config_id)
            .one_or_none()
        )

        if not draft_config:
            raise NotFoundException("应用配置不存在")

        with self.db.auto_commit():
            new_app = App(
                account_id=account.id,
                name=f"{app.name} - 复制",
                icon=app.icon,
                description=app.description,
                status=AppStatus.DRAFT,
            )
            self.db.session.add(new_app)
            self.db.session.flush()

            new_draft_config = AppConfigVersion(
                app_id=new_app.id,
                model_config=draft_config.model_config,
                dialog_round=draft_config.dialog_round,
                preset_prompt=draft_config.preset_prompt,
                tools=draft_config.tools,
                workflows=draft_config.workflows,
                datasets=draft_config.datasets,
                retrieval_config=draft_config.retrieval_config,
                long_term_memory=draft_config.long_term_memory,
                opening_statement=draft_config.opening_statement,
                opening_questions=draft_config.opening_questions,
                speech_to_text=draft_config.speech_to_text,
                text_to_speech=draft_config.text_to_speech,
                suggested_after_answer=draft_config.suggested_after_answer,
                review_config=draft_config.review_config,
                version=0,
                config_type=AppConfigType.DRAFT,
            )
            self.db.session.add(new_draft_config)
            self.db.session.flush()

            new_app.draft_app_config_id = new_draft_config.id
        return new_app.id

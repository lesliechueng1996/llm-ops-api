"""
@Time   : 2025/01/06 20:11
@Author : Leslie
@File   : app_config_serice.py
"""

from dataclasses import dataclass
import logging
from typing import Any, Union
from uuid import UUID
from flask import request
from injector import inject
from internal.core.tools.api_tools.entities.tool_entity import ToolEntity
from internal.core.tools.api_tools.providers.api_provider_manager import (
    ApiProviderManager,
)
from internal.core.tools.builtin_tools.providers.builtin_provider_manager import (
    BuiltinProviderManager,
)
from internal.entity.app_entity import AppConfigType
from internal.exception.exception import NotFoundException
from internal.lib.helper import datetime_to_timestamp
from internal.model.account import Account
from internal.model.api_tool import ApiTool, ApiToolProvider
from internal.model.app import App, AppConfig, AppConfigVersion
from internal.model.dataset import Dataset
from pkg.sqlalchemy import SQLAlchemy
from langchain_core.tools import BaseTool


@inject
@dataclass
class AppConfigService:
    db: SQLAlchemy
    builtin_provider_manager: BuiltinProviderManager
    api_provider_manager: ApiProviderManager

    def get_draft_app_config(self, app: App) -> dict[str, Any]:
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
            raise NotFoundException("应用配置不存在")

        validate_tools, tools = self._process_validate_tools(app_config_version.tools)

        if validate_tools != app_config_version.tools:
            logging.warning(f"应用配置中存在无效工具")
            with self.db.auto_commit():
                app_config_version.tools = validate_tools

        validate_datasets, datasets = self._process_validate_datasets(
            app_config_version.datasets
        )

        if len(validate_datasets) != len(app_config_version.datasets):
            logging.warning("应用配置中存在无效知识库")
            with self.db.auto_commit():
                app_config_version.datasets = [
                    dataset.id for dataset in validate_datasets
                ]

        # TODO 校验工作流

        return self._process_transform_app_config(
            tools, [], datasets, app_config_version
        )

    def get_app_config(self, app: App) -> dict[str, Any]:
        pass

    def get_langchain_tools_by_tool_config(
        self, tool_config: list[dict], account: Account
    ) -> list[BaseTool]:
        tools = []
        for tool in tool_config:
            if tool["type"] == "builtin_tool":
                builtin_tool = self.builtin_provider_manager.get_tool(
                    tool["provider"]["id"],
                    tool["tool"]["name"],
                )
                if not builtin_tool:
                    continue
                tools.append(builtin_tool(**tool["tool"]["params"]))
            if tool["type"] == "api_tool":
                api_tool_record = (
                    self.db.session.query(ApiTool)
                    .filter(
                        ApiTool.account_id == account.id,
                        ApiTool.id == tool["tool"]["id"],
                    )
                    .one_or_none()
                )
                if not api_tool_record:
                    continue
                api_tool_provider_record = (
                    self.db.session.query(ApiToolProvider)
                    .filter(
                        ApiToolProvider.id == api_tool_record.provider_id,
                    )
                    .one_or_none()
                )
                if not api_tool_provider_record:
                    continue
                api_tool = self.api_provider_manager.get_tool(
                    ToolEntity(
                        provider_id=str(api_tool_record.provider_id),
                        name=api_tool_record.name,
                        url=api_tool_record.url,
                        method=api_tool_record.method,
                        description=api_tool_record.description,
                        headers=api_tool_provider_record.headers,
                        parameters=api_tool_record.parameters,
                    )
                )
                tools.append(api_tool)

        return tools

    def _process_validate_tools(
        self, original_tools: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        # 校验工具
        validate_tools = []
        tools = []
        for tool in original_tools:
            if tool["type"] == "builtin_tool":
                provider = self.builtin_provider_manager.get_provider(
                    tool["provider_id"]
                )
                if not provider:
                    continue
                tool_entity = provider.get_tool_entity(tool["tool_id"])
                if not tool_entity:
                    continue

                tool_params = set([param.name for param in tool_entity.params])
                params = tool["params"]
                if set(tool["params"].keys()) - tool_params:
                    params = {
                        param.name: param.default
                        for param in tool_entity.params
                        if param.default is not None
                    }

                provider_entity = provider.provider_entity
                validate_tools.append(
                    {
                        **tool,
                        "params": params,
                    }
                )
                tools.append(
                    {
                        "type": "builtin_tool",
                        "provider": {
                            "id": provider_entity.name,
                            "name": provider_entity.name,
                            "label": provider_entity.label,
                            "icon": f"{request.scheme}://{request.host}/builtin-tools/{provider_entity.name}/icon",
                            "description": provider_entity.description,
                        },
                        "tool": {
                            "id": tool_entity.name,
                            "name": tool_entity.name,
                            "label": tool_entity.label,
                            "description": tool_entity.description,
                            "params": tool["params"],
                        },
                    }
                )
            if tool["type"] == "api_tool":
                tool_record = (
                    self.db.session.query(ApiTool)
                    .filter(
                        ApiTool.provider_id == tool["provider_id"],
                        ApiTool.id == tool["tool_id"],
                    )
                    .one_or_none()
                )
                if not tool_record:
                    continue

                tool_provider = (
                    self.db.session.query(ApiToolProvider)
                    .filter(ApiToolProvider.id == tool_record.provider_id)
                    .one_or_none()
                )

                if not tool_provider:
                    continue

                validate_tools.append(tool)
                tools.append(
                    {
                        "type": "api_tool",
                        "provider": {
                            "id": str(tool_provider.id),
                            "name": tool_record.name,
                            "label": tool_record.name,
                            "icon": tool_provider.icon,
                            "description": tool_provider.description,
                        },
                        "tool": {
                            "id": str(tool_record.id),
                            "name": tool_record.name,
                            "label": tool_record.name,
                            "description": tool_record.description,
                            "params": {},
                        },
                    }
                )

        return validate_tools, tools

    def _process_validate_datasets(self, original_datasets: list[UUID]) -> list[dict]:
        datasets = []
        dataset_records = (
            self.db.session.query(Dataset)
            .filter(
                Dataset.id.in_(original_datasets),
            )
            .all()
        )
        dataset_map = {str(dataset.id): dataset for dataset in dataset_records}
        dataset_sets = set(dataset_map.keys())

        validate_datasets = [
            dataset_id for dataset_id in original_datasets if dataset_id in dataset_sets
        ]

        for dataset_id in validate_datasets:
            dataset = dataset_map.get(dataset_id)
            datasets.append(
                {
                    "id": dataset.id,
                    "name": dataset.name,
                    "icon": dataset.icon,
                    "description": dataset.description,
                }
            )

        return validate_datasets, datasets

    def _process_transform_app_config(
        self,
        tools: list[dict],
        workflows: list[dict],
        datasets: list[dict],
        app_config: Union[AppConfigVersion, AppConfig],
    ) -> dict[str, Any]:
        return {
            "id": str(app_config.id),
            "model_config": app_config.model_config,
            "dialog_round": app_config.dialog_round,
            "preset_prompt": app_config.preset_prompt,
            "tools": tools,
            "workflows": workflows,
            "datasets": datasets,
            "retrieval_config": app_config.retrieval_config,
            "long_term_memory": app_config.long_term_memory,
            "opening_statement": app_config.opening_statement,
            "opening_questions": app_config.opening_questions,
            "speech_to_text": app_config.speech_to_text,
            "text_to_speech": app_config.text_to_speech,
            "suggested_after_answer": app_config.suggested_after_answer,
            "review_config": app_config.review_config,
            "created_at": datetime_to_timestamp(app_config.created_at),
            "updated_at": datetime_to_timestamp(app_config.updated_at),
        }

"""
@Time   : 2024/12/13 12:03
@Author : Leslie
@File   : api_tool_service.py
"""

import json
from injector import inject
from dataclasses import dataclass
from internal.exception import ValidateErrorException, NotFoundException
from internal.core.tools.api_tools.entities import OpenAPISchema, ToolEntity
from internal.schema import (
    CreateAPIToolsSchemaReq,
    GetToolsPaginationSchemaReq,
    UpdateAPIToolsSchemaReq,
)
from pkg.sqlalchemy import SQLAlchemy
from internal.model import ApiToolProvider, ApiTool
from pkg.pagination import Paginator
from sqlalchemy import desc
from internal.core.tools.api_tools.providers import ApiProviderManger


@inject
@dataclass
class ApiToolService:
    db: SQLAlchemy
    api_provider_manager: ApiProviderManger

    def validate_openapi_schema(self, openapi_schema_str: str):
        try:
            openapi_schema = json.loads(openapi_schema_str)
            if not isinstance(openapi_schema, dict):
                raise
        except Exception as e:
            raise ValidateErrorException("传递的openapi schema不是一个合法的json字符串")

        return OpenAPISchema(**openapi_schema)

    def create_api_tools(self, data: CreateAPIToolsSchemaReq):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        openapi_schema = self.validate_openapi_schema(data.openapi_schema.data)

        tool_provider = (
            self.db.session.query(ApiToolProvider)
            .filter_by(
                account_id=account_id,
                name=data.name.data,
            )
            .one_or_none()
        )

        if tool_provider:
            raise ValidateErrorException(f"工具提供商: {data.name.data}已经存在")

        with self.db.auto_commit():
            api_tool_provider = ApiToolProvider(
                account_id=account_id,
                name=data.name.data,
                icon=data.icon.data,
                openapi_schema=json.dumps(
                    openapi_schema.model_dump(), ensure_ascii=False
                ),
                headers=data.headers.data,
            )
            self.db.session.add(api_tool_provider)
            self.db.session.flush()

            tools = []
            for path, path_item in openapi_schema.paths.items():
                for method, method_item in path_item.items():
                    tools.append(
                        ApiTool(
                            account_id=account_id,
                            provider_id=api_tool_provider.id,
                            name=method_item.get("operationId"),
                            description=method_item.get("description"),
                            url=f"{openapi_schema.server}{path}",
                            method=method,
                            parameters=method_item.get("parameters"),
                        )
                    )
            self.db.session.add_all(tools)
        pass

    def get_api_tools_provider(self, provider_id: str) -> ApiToolProvider:
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        provider = (
            self.db.session.query(ApiToolProvider)
            .filter_by(
                id=provider_id,
                account_id=account_id,
            )
            .one_or_none()
        )

        if not provider:
            raise NotFoundException("工具提供商不存在")

        return provider

    def get_api_tool(self, provider_id: str, tool_name: str) -> ApiTool:
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        tool = (
            self.db.session.query(ApiTool)
            .filter_by(
                provider_id=provider_id,
                account_id=account_id,
                name=tool_name,
            )
            .one_or_none()
        )

        if not tool:
            raise NotFoundException("工具不存在")

        return tool

    def delete_api_tool_provider(self, provider_id: str):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        with self.db.auto_commit():
            self.db.session.query(ApiToolProvider).filter_by(
                id=provider_id, account_id=account_id
            ).delete()
            self.db.session.query(ApiTool).filter_by(
                provider_id=provider_id, account_id=account_id
            ).delete()
        return

    def get_api_tools_pagination(self, req: GetToolsPaginationSchemaReq):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        filters = [ApiToolProvider.account_id == account_id]
        if req.search_word.data:
            filters.append(ApiToolProvider.name.ilike(f"%{req.search_word.data}%"))

        query = (
            self.db.session.query(ApiToolProvider)
            .filter(*filters)
            .order_by(desc("created_at"))
        )
        paginator = Paginator(self.db, req)
        providers = paginator.paginate(query)

        return providers, paginator

    def update_api_tools_provider(self, req: UpdateAPIToolsSchemaReq, provider_id: str):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        openapi_schema = self.validate_openapi_schema(req.openapi_schema.data)
        provider = self.get_api_tools_provider(provider_id)

        same_name_providers = (
            self.db.session.query(ApiToolProvider)
            .filter(
                ApiToolProvider.account_id == account_id,
                ApiToolProvider.name == req.name.data,
                ApiToolProvider.id != provider_id,
            )
            .all()
        )
        if same_name_providers:
            raise ValidateErrorException("工具提供商名称已经存在")

        with self.db.auto_commit():
            provider.name = req.name.data
            provider.icon = req.icon.data
            provider.headers = req.headers.data
            provider.openapi_schema = json.dumps(
                openapi_schema.model_dump(), ensure_ascii=False
            )

            self.db.session.query(ApiTool).filter_by(
                provider_id=provider_id, account_id=account_id
            ).delete()

            tools = []
            for path, path_item in openapi_schema.paths.items():
                for method, method_item in path_item.items():
                    tools.append(
                        ApiTool(
                            account_id=account_id,
                            provider_id=provider.id,
                            name=method_item.get("operationId"),
                            description=method_item.get("description"),
                            url=f"{openapi_schema.server}{path}",
                            method=method,
                            parameters=method_item.get("parameters"),
                        )
                    )
            self.db.session.add_all(tools)

    def invoke_api_tool(self, provider_id: str, tool_name: str):
        tool = self.get_api_tool(provider_id, tool_name)
        provider = self.get_api_tools_provider(provider_id)
        tool_entity = ToolEntity(
            provider_id=provider_id,
            name=tool.name,
            url=tool.url,
            method=tool.method,
            description=tool.description,
            headers=provider.headers,
            parameters=tool.parameters,
        )
        tool_func = self.api_provider_manager.get_tool(tool_entity=tool_entity)
        return tool_func.invoke({"q": "love", "doctype": "json"})

"""
@Time   : 2024/12/13 12:00
@Author : Leslie
@File   : api_tool_handler.py
"""

from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.schema import (
    ValidationOpenAPISchemaReq,
    CreateAPIToolsSchemaReq,
    GetAPIToolsProviderSchemaRes,
    GetAPIToolSchemaRes,
    GetToolsPaginationSchemaReq,
    GetToolsPaginationItemSchemaRes,
)
from internal.service import ApiToolService
from pkg.response import validate_error_json, success_message, success_json
from flask import request
from pkg.pagination import PageModel


@inject
@dataclass
class ApiToolHandler:
    api_tool_service: ApiToolService

    def validate_openapi_schema(self):
        req = ValidationOpenAPISchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.api_tool_service.validate_openapi_schema(req.openapi_schema.data)
        return success_message("openapi schema验证通过")

    def create_api_tools(self):
        req = CreateAPIToolsSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)

        self.api_tool_service.create_api_tools(req)
        return success_message("创建api tools成功")

    def get_api_tools_provider(self, provider_id: UUID):
        provider = self.api_tool_service.get_api_tools_provider(provider_id)
        res_schema = GetAPIToolsProviderSchemaRes()
        return success_json(res_schema.dump(provider))

    def get_api_tool(self, provider_id: UUID, tool_name: str):
        api_tool = self.api_tool_service.get_api_tool(provider_id, tool_name)
        res_schema = GetAPIToolSchemaRes()
        return success_json(res_schema.dump(api_tool))

    def delete_api_tool_provider(self, provider_id: UUID):
        self.api_tool_service.delete_api_tool_provider(provider_id)
        return success_message("删除api tool provider成功")

    def get_api_tools_pagination(self):
        req = GetToolsPaginationSchemaReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        schema = GetToolsPaginationItemSchemaRes(many=True)

        list, paginator = self.api_tool_service.get_api_tools_pagination(req)
        dump_list = schema.dump(list)
        return success_json(PageModel(dump_list, paginator))

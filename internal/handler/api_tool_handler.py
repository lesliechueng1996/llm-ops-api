"""
@Time   : 2024/12/13 12:00
@Author : Leslie
@File   : api_tool_handler.py
"""

from injector import inject
from dataclasses import dataclass
from internal.schema import ValidationOpenAPISchemaReq
from internal.service import ApiToolService
from pkg.response import validate_error_json, success_message


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

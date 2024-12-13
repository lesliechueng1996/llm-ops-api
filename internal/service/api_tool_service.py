"""
@Time   : 2024/12/13 12:03
@Author : Leslie
@File   : api_tool_service.py
"""

import json
from injector import inject
from dataclasses import dataclass
from internal.exception import ValidateErrorException
from internal.core.tools.api_tools.entities import OpenAPISchema


@inject
@dataclass
class ApiToolService:
    def validate_openapi_schema(self, openapi_schema_str: str):
        try:
            openapi_schema = json.loads(openapi_schema_str)
            if not isinstance(openapi_schema, dict):
                raise
        except Exception as e:
            raise ValidateErrorException("传递的openapi schema不是一个合法的json字符串")

        return OpenAPISchema(**openapi_schema)

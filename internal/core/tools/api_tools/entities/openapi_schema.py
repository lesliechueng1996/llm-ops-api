"""
@Time   : 2024/12/13 12:13
@Author : Leslie
@File   : openapi_schema.py
"""

from pydantic import BaseModel, Field, field_validator
from internal.exception import ValidateErrorException
from enum import Enum


class ParameterIn(str, Enum):
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"
    REQUEST_BODY = "request_body"


class ParameterType(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"


class OpenAPISchema(BaseModel):
    server: str = Field(
        default="", description="工具提供者的服务基础地址", validate_default=True
    )
    description: str = Field(
        default="", description="工具提供者的描述信息", validate_default=True
    )
    paths: dict[str, dict] = Field(
        default_factory=dict,
        description="工具提供者的接口路径及参数字典",
        validate_default=True,
    )

    @field_validator("server", mode="before")
    def validate_server(cls, server: str):
        if server is None or server.strip() == "":
            raise ValidateErrorException("server不能为空")
        return server

    @field_validator("description", mode="before")
    def validate_description(cls, description: str):
        if description is None or description.strip() == "":
            raise ValidateErrorException("description不能为空")
        return description

    @field_validator("paths", mode="before")
    def validate_paths(cls, paths: dict[str, dict]):
        if not paths or not isinstance(paths, dict):
            raise ValidateErrorException("paths不能为空, 且必须是一个字典")

        allowed_methods = ["get", "post", "put", "delete", "patch"]
        apis = []
        for path, path_item in paths.items():
            for method in path_item.keys():
                if method in allowed_methods:
                    apis.append(
                        {
                            "path": path,
                            "method": method,
                            "operation": path_item[method],
                        },
                    )

        operationIds = []
        results = {}
        for api in apis:
            operationId = api["operation"].get("operationId")
            description = api["operation"].get("description")
            parameters = api["operation"].get("parameters", [])
            if not isinstance(operationId, str) or operationId.strip() == "":
                raise ValidateErrorException("operationId必须为字符串且不能为空")
            if not isinstance(description, str) or description.strip() == "":
                raise ValidateErrorException("description必须为字符串且不能为空")
            if not isinstance(parameters, list):
                raise ValidateErrorException("parameters必须为列表")
            if operationId in operationIds:
                raise ValidateErrorException(f"operationId: {operationId}不能重复")
            operationIds.append(operationId)

            for parameter in parameters:
                if (
                    not isinstance(parameter.get("name"), str)
                    or parameter.get("name").strip() == ""
                ):
                    raise ValidateErrorException("parameter.name必须为字符串且不能为空")
                if (
                    not isinstance(parameter.get("in"), str)
                    or parameter.get("in") not in ParameterIn.__members__.values()
                ):
                    raise ValidateErrorException(
                        f"parameter.in必须为{'/'.join([item.value for item in ParameterIn])}之一"
                    )
                if (
                    not isinstance(parameter.get("description"), str)
                    or parameter.get("description").strip() == ""
                ):
                    raise ValidateErrorException(
                        "parameter.description必须为字符串且不能为空"
                    )
                if not isinstance(parameter.get("required"), bool):
                    raise ValidateErrorException("parameter.required必须为布尔值")
                if (
                    not isinstance(parameter.get("type"), str)
                    or parameter.get("type") not in ParameterType.__members__.values()
                ):
                    raise ValidateErrorException(
                        f"parameter.type必须为{'/'.join([item.value for item in ParameterType])}之一"
                    )

        results[api["path"]] = {
            api["method"]: {
                "operationId": operationId,
                "description": description,
                "parameters": [
                    {
                        "name": parameter.get("name"),
                        "in": parameter.get("in"),
                        "description": parameter.get("description"),
                        "required": parameter.get("required"),
                        "type": parameter.get("type"),
                    }
                    for parameter in parameters
                ],
            }
        }
        return results

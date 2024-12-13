"""
@Time   : 2024/12/14 01:18
@Author : Leslie
@File   : api_provider_manager.py
"""

from dataclasses import dataclass
import requests
from injector import inject
from langchain_core.tools import BaseTool, StructuredTool
from internal.core.tools.api_tools.entities import ToolEntity
from pydantic import create_model, Field, BaseModel
from typing import Optional, Type
from internal.core.tools.api_tools.entities import ParameterTypeMap, ParameterIn


@inject
@dataclass
class ApiProviderManger:
    def _create_tool_func_from_entity(self, tool_entity: ToolEntity):
        def tool_func(**kwargs):
            params = {
                ParameterIn.PATH: {},
                ParameterIn.QUERY: {},
                ParameterIn.HEADER: {},
                ParameterIn.COOKIE: {},
                ParameterIn.REQUEST_BODY: {},
            }

            allowed_params = {
                parameter["name"]: parameter for parameter in tool_entity.parameters
            }

            provider_headers = {
                header["key"]: header["value"] for header in tool_entity.headers
            }

            for key, value in kwargs.items():
                mapping_param = allowed_params.get(key)
                param_in = mapping_param["in"]
                params[param_in][key] = value

            return requests.request(
                method=tool_entity.method,
                url=tool_entity.url.format(**params[ParameterIn.PATH]),
                headers={**provider_headers, **params[ParameterIn.HEADER]},
                params=params[ParameterIn.QUERY],
                cookies=params[ParameterIn.COOKIE],
                json=params[ParameterIn.REQUEST_BODY],
            ).text

        return tool_func

    def _create_model_from_entity(self, tool_entity: ToolEntity) -> Type[BaseModel]:
        fields = {}
        for parameter in tool_entity.parameters:
            field_name = parameter["name"]
            field_type = ParameterTypeMap.get(parameter["type"], str)
            field_required = parameter["required"]
            field_description = parameter["description"]

            fields[field_name] = (
                field_type if field_required else Optional[field_type],
                Field(description=field_description),
            )

        return create_model("DynamicModel", **fields)

    def get_tool(self, tool_entity: ToolEntity) -> BaseTool:
        return StructuredTool.from_function(
            func=self._create_tool_func_from_entity(tool_entity),
            name=f"{tool_entity.provider_id}_{tool_entity.name}",
            description=tool_entity.description,
            args_schema=self._create_model_from_entity(tool_entity),
        )

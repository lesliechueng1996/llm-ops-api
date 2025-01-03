"""
@Time   : 2024/12/13 11:56
@Author : Leslie
@File   : api_tool_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL, Optional

from pkg.pagination import PaginationReq
from .schema import ListField
from internal.exception import ValidateErrorException
from marshmallow import Schema, fields, pre_dump
from internal.model import ApiToolProvider, ApiTool


class ValidationOpenAPISchemaReq(FlaskForm):
    openapi_schema = StringField(
        "openapi_schema",
        validators=[
            DataRequired(message="openapi_schema字段不能为空"),
        ],
    )


class CreateAPIToolsSchemaReq(FlaskForm):
    name = StringField(
        "name",
        validators=[
            DataRequired(message="工具提供者名字不能为空"),
            Length(min=1, max=30, message="工具提供者的名字长度在1-30"),
        ],
    )
    icon = StringField(
        "icon",
        validators=[
            DataRequired(message="工具提供商图标不能为空"),
            URL(message="工具提供商图标必须是一个URL"),
        ],
    )
    description = StringField(
        "description",
        validators=[
            DataRequired(message="工具提供商描述不能为空"),
            Length(min=1, max=100, message="工具提供商描述长度在1-100"),
        ],
    )
    openapi_schema = StringField(
        "openapi_schema",
        validators=[
            DataRequired(message="openapi_schema字段不能为空"),
        ],
    )
    headers = ListField("headers", default=[])

    @classmethod
    def validate_headers(cls, form, field):
        for header in field.data:
            if not isinstance(header, dict):
                raise ValidateErrorException("headers字段必须是一个字典列表")
            if set(header.keys()) != {"key", "value"}:
                raise ValidateErrorException("headers字段必须只包含key和value字段")


class GetAPIToolsProviderSchemaRes(Schema):
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    description = fields.String()
    openapi_schema = fields.String()
    headers = fields.List(fields.Dict(), default=[])
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data: ApiToolProvider, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "openapi_schema": data.openapi_schema,
            "description": data.description,
            "headers": data.headers,
            "created_at": int(data.created_at.timestamp()),
        }


class GetAPIToolSchemaRes(Schema):
    id = fields.UUID()
    name = fields.String()
    description = fields.String()
    inputs = fields.List(fields.Dict(), default=[])
    provider = fields.Dict()

    @pre_dump
    def process_data(self, data: ApiTool, **kwargs):
        provider = data.provider
        return {
            "id": data.id,
            "name": data.name,
            "description": data.description,
            "inputs": [
                {key: value for key, value in parameter.items() if key != "in"}
                for parameter in data.parameters
            ],
            "provider": {
                "id": provider.id,
                "name": provider.name,
                "icon": provider.icon,
                "description": provider.description,
                "headers": provider.headers,
            },
        }


class GetToolsPaginationSchemaReq(PaginationReq):
    search_word = StringField("search_word", default="", validators=[Optional()])


class GetToolsPaginationItemSchemaRes(Schema):
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    tools = fields.List(fields.Dict(), default=[])
    description = fields.String()
    headers = fields.List(fields.Dict(), default=[])
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data, **kwargs):
        return {
            "id": data.id,
            "name": data.name,
            "icon": data.icon,
            "tools": [
                {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "inputs": [
                        {k: v for k, v in parameter.items() if k != "in"}
                        for parameter in tool.parameters
                    ],
                }
                for tool in data.tools
            ],
            "description": data.description,
            "headers": data.headers,
            "created_at": int(data.created_at.timestamp()),
        }


class UpdateAPIToolsSchemaReq(FlaskForm):
    name = StringField(
        "name",
        validators=[
            DataRequired(message="工具提供者名字不能为空"),
            Length(min=1, max=30, message="工具提供者的名字长度在1-30"),
        ],
    )
    icon = StringField(
        "icon",
        validators=[
            DataRequired(message="工具提供商图标不能为空"),
            URL(message="工具提供商图标必须是一个URL"),
        ],
    )
    openapi_schema = StringField(
        "openapi_schema",
        validators=[
            DataRequired(message="openapi_schema字段不能为空"),
        ],
    )

    description = StringField(
        "description",
        validators=[
            DataRequired(message="工具提供商描述不能为空"),
            Length(min=1, max=100, message="工具提供商描述长度在1-100"),
        ],
    )
    headers = ListField("headers", default=[])

    @classmethod
    def validate_headers(cls, form, field):
        for header in field.data:
            if not isinstance(header, dict):
                raise ValidateErrorException("headers字段必须是一个字典列表")
            if set(header.keys()) != {"key", "value"}:
                raise ValidateErrorException("headers字段必须只包含key和value字段")

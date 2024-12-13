"""
@Time   : 2024/12/13 11:56
@Author : Leslie
@File   : api_tool_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL
from .schema import ListField
from internal.exception import ValidateErrorException


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

"""
@Time   : 2025/01/05 21:53
@Author : Leslie
@File   : api_key_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import Length, Optional
from internal.exception.exception import ValidateErrorException
from marshmallow import Schema, fields, pre_dump
from internal.model import ApiKey
from internal.lib.helper import datetime_to_timestamp


class CreateApiKeyReqSchema(FlaskForm):
    is_active = BooleanField("is_active")

    remark = StringField(
        "remark",
        validators=[
            Optional(),
            Length(
                min=0,
                max=100,
                message="remark长度必须在0到100之间",
            ),
        ],
    )

    def validate_is_active(self, field: BooleanField):
        if not isinstance(field.data, bool):
            raise ValidateErrorException("is_active字段必须是布尔值")


class UpdateApiKeyReqSchema(FlaskForm):
    is_active = BooleanField("is_active")

    remark = StringField(
        "remark",
        validators=[
            Optional(),
            Length(
                min=0,
                max=100,
                message="remark长度必须在0到100之间",
            ),
        ],
    )

    def validate_is_active(self, field: BooleanField):
        if not isinstance(field.data, bool):
            raise ValidateErrorException("is_active字段必须是布尔值")


class UpdateApiKeyActiveReqSchema(FlaskForm):
    is_active = BooleanField("is_active")

    def validate_is_active(self, field: BooleanField):
        if not isinstance(field.data, bool):
            raise ValidateErrorException("is_active字段必须是布尔值")


class GetApiKeysPaginationResSchema(Schema):
    id = fields.UUID()
    api_key = fields.String()
    is_active = fields.Boolean()
    remark = fields.String()
    updated_at = fields.Integer()
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data: ApiKey, **kwargs):
        return {
            "id": data.id,
            "api_key": data.api_key,
            "is_active": data.is_active,
            "remark": data.remark,
            "updated_at": datetime_to_timestamp(data.updated_at),
            "created_at": datetime_to_timestamp(data.created_at),
        }

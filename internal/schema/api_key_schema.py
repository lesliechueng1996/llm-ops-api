"""
@Time   : 2025/01/05 21:53
@Author : Leslie
@File   : api_key_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import Length, Optional

from internal.exception.exception import ValidateErrorException


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

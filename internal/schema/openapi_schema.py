"""
@Time   : 2025/01/06 22:23
@Author : Leslie
@File   : openapi_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired, UUID, Optional
import uuid
from internal.exception import ValidateErrorException


class OpenapiChatReqSchema(FlaskForm):
    app_id = StringField(
        "app_id",
        validators=[
            DataRequired(message="app_id不能为空"),
            UUID(message="app_id格式错误"),
        ],
    )

    end_user_id = StringField(
        "end_user_id", validators=[Optional(), UUID(message="end_user_id格式错误")]
    )

    conversation_id = StringField("conversation_id")

    query = StringField("query", validators=[DataRequired(message="query不能为空")])

    stream = BooleanField("stream")

    def validate_conversation_id(self, field: StringField):
        if field.data:
            try:
                uuid.UUID(field.data)
            except Exception as _:
                raise ValidateErrorException("conversation_id 格式错误")

            if not self.end_user_id.data:
                raise ValidateErrorException(
                    "传递 conversation_id 时，end_user_id 不能为空"
                )

    def validate_stream(self, field: BooleanField):
        if not isinstance(field.data, bool):
            raise ValidateErrorException("stream 格式错误")

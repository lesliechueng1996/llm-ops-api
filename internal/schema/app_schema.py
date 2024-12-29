"""
@Time   : 2024/12/1 19:35
@Author : Leslie
@File   : app_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL, Optional
from marshmallow import Schema, fields, pre_dump
from internal.lib.helper import datetime_to_timestamp


class CompletionReq(FlaskForm):
    query = StringField(
        "query",
        validators=[
            DataRequired(message="请输入用户问题"),
            Length(max=2000, message="用户问题不能超过2000字符"),
        ],
    )


class CreateAppReqSchema(FlaskForm):
    name = StringField(
        "name",
        validators=[
            DataRequired(message="请输入应用名称"),
            Length(max=40, message="应用名称不能超过40字符"),
        ],
    )

    icon = StringField(
        "icon",
        validators=[
            DataRequired(message="请输入应用图标"),
            URL(message="应用图标格式不正确"),
        ],
    )

    description = StringField(
        "description",
        validators=[Optional(), Length(max=800, message="应用描述不能超过800字符")],
    )


class GetAppResSchema(Schema):
    id = fields.UUID()
    debug_conversation_id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    description = fields.String()
    status = fields.String()
    draft_updated_at = fields.Integer()
    updated_at = fields.Integer()
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data: dict, **kwargs):
        app = data["app"]
        return {
            "id": app.id,
            "debug_conversation_id": app.debug_conversation_id,
            "name": app.name,
            "icon": app.icon,
            "description": app.description or "",
            "status": app.status,
            "draft_updated_at": datetime_to_timestamp(data["draft_updated_at"]),
            "updated_at": datetime_to_timestamp(app.updated_at),
            "created_at": datetime_to_timestamp(app.created_at),
        }

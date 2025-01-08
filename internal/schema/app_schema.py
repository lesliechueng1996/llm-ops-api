"""
@Time   : 2024/12/1 19:35
@Author : Leslie
@File   : app_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Length, URL, Optional, NumberRange
from marshmallow import Schema, fields, pre_dump
from internal.lib.helper import datetime_to_timestamp
from internal.model.app import App, AppConfigVersion
from pkg.pagination import PaginationReq


class DebugChatRequestSchema(FlaskForm):
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


class GetAppConfigPublishHistoriesResSchema(Schema):
    id = fields.UUID()
    version = fields.String()
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data: AppConfigVersion, **kwargs):
        return {
            "id": data.id,
            "version": data.version,
            "created_at": datetime_to_timestamp(data.created_at),
        }


class FallbackHistoryReqSchema(FlaskForm):
    app_config_version_id = StringField(
        "app_config_version_id",
        validators=[
            DataRequired(message="请输入版本ID"),
        ],
    )


class UpdateAppDebugSummaryReqSchema(FlaskForm):
    summary = StringField("summary")


class GetConversationMessagesReqSchema(PaginationReq):
    created_at = IntegerField(
        "created_at",
        validators=[Optional(), NumberRange(min=0, message="created_at必须大于等于0")],
    )


class UpdateAppReqSchema(FlaskForm):
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


class GetAppDebugSummaryReqSchema(PaginationReq):
    search_word = StringField("search_word", validators=[Optional()])


class GetAppDebugSummaryResSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    description = fields.String()
    preset_prompt = fields.String()
    model_config = fields.Dict()
    status = fields.String()
    updated_at = fields.Integer()
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data: dict, **kwargs):
        app: App = data["app"]
        preset_prompt: str = data["preset_prompt"]
        provider: str = data["provider"]
        model: str = data["model"]

        return {
            "id": app.id,
            "name": app.name,
            "icon": app.icon,
            "description": app.description or "",
            "preset_prompt": preset_prompt,
            "model_config": {
                "provider": provider,
                "model": model,
            },
            "status": app.status,
            "updated_at": datetime_to_timestamp(app.updated_at),
            "created_at": datetime_to_timestamp(app.created_at),
        }

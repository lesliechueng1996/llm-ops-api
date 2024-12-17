"""
@Time   : 2024/12/18 01:11
@Author : Leslie
@File   : dataset_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL, Optional
from marshmallow import Schema, fields, pre_dump


class CreateDatasetSchemaReq(FlaskForm):
    name = StringField(
        "name",
        validators=[
            DataRequired(message="知识库名称不能为空"),
            Length(max=100, message="知识库名称不能超过100字符"),
        ],
    )

    icon = StringField(
        "icon",
        validators=[
            DataRequired(message="知识库图标不能为空"),
            URL(message="知识库图标必须是图片URL地址"),
        ],
    )

    description = StringField(
        "description",
        validators=[
            Optional(),
            Length(max=2000, message="知识库描述不能超过2000字符"),
        ],
    )


class UpdateDatasetSchemaReq(FlaskForm):
    name = StringField(
        "name",
        validators=[
            DataRequired(message="知识库名称不能为空"),
            Length(max=100, message="知识库名称不能超过100字符"),
        ],
    )

    icon = StringField(
        "icon",
        validators=[
            DataRequired(message="知识库图标不能为空"),
            URL(message="知识库图标必须是图片URL地址"),
        ],
    )

    description = StringField(
        "description",
        validators=[
            Optional(),
            Length(max=2000, message="知识库描述不能超过2000字符"),
        ],
    )


class GetDatasetSchemaRes(Schema):
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    description = fields.String()
    document_count = fields.Integer()
    hit_count = fields.Integer()
    related_app_count = fields.Integer()
    character_count = fields.Integer()
    updated_at = fields.Integer()
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data: dict, **kwargs):
        return {
            **data,
            "updated_at": int(data["updated_at"].timestamp()),
            "created_at": int(data["created_at"].timestamp()),
        }

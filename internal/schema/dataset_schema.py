"""
@Time   : 2024/12/18 01:11
@Author : Leslie
@File   : dataset_schema.py
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, URL, Optional, AnyOf, NumberRange
from marshmallow import Schema, fields, pre_dump
from pkg.pagination import PaginationReq
from internal.entity import RetrievalStrategy


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


class GetDatasetsPaginationSchemaReq(PaginationReq):
    search_word = StringField(
        "search_word",
        default="",
        validators=[
            Optional(),
        ],
    )


class GetDatasetsPaginationItemSchemaRes(Schema):
    id = fields.UUID()
    name = fields.String()
    icon = fields.String()
    description = fields.String()
    document_count = fields.Integer()
    character_count = fields.Integer()
    related_app_count = fields.Integer()
    updated_at = fields.Integer()
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data: dict, **kwargs):
        return {
            **data,
            "updated_at": int(data["updated_at"].timestamp()),
            "created_at": int(data["created_at"].timestamp()),
        }


class HitDatasetSchemaReq(FlaskForm):
    query = StringField(
        "query",
        validators=[
            DataRequired(message="查询内容不能为空"),
            Length(max=200, message="查询内容不能超过200字符"),
        ],
    )
    retrieval_strategy = StringField(
        "retrieval_strategy",
        validators=[
            DataRequired(message="检索策略不能为空"),
            AnyOf(
                [strategy.value for strategy in RetrievalStrategy],
                message="检索策略不合法",
            ),
        ],
    )
    k = IntegerField(
        "k",
        validators=[
            DataRequired(message="k值不能为空"),
            NumberRange(min=1, max=10, message="k值必须在1-10之间"),
        ],
    )
    score = FloatField(
        "score",
        validators=[
            NumberRange(min=0, max=0.99, message="得分必须在0-0.99之间"),
        ],
    )

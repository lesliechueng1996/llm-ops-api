"""
@Time   : 2024/12/21 17:06
@Author : Leslie
@File   : segment_schema.py
"""

from pkg.pagination import PaginationReq
from wtforms import StringField
from wtforms.validators import Optional
from marshmallow import Schema, fields, pre_dump
from internal.model import Segment
from internal.lib.helper import datetime_to_timestamp


class GetSegmentsPaginationSchemaReq(PaginationReq):
    search_word = StringField("search_word", default="", validators=[Optional()])


class GetSegmentsPaginationItemSchemaRes(Schema):
    id = fields.UUID()
    dataset_id = fields.UUID()
    document_id = fields.UUID()
    position = fields.Integer()
    content = fields.String()
    keywords = fields.List(fields.String())
    character_count = fields.Integer()
    token_count = fields.Integer()
    hit_count = fields.Integer()
    enabled = fields.Boolean()
    disabled_at = fields.Integer()
    status = fields.String()
    error = fields.String()
    updated_at = fields.Integer()
    created_at = fields.Integer()

    @pre_dump
    def process_data(self, data: Segment, **kwargs):
        return {
            "id": data.id,
            "dataset_id": data.dataset_id,
            "document_id": data.document_id,
            "position": data.position,
            "content": data.content,
            "keywords": data.keywords,
            "character_count": data.character_count,
            "token_count": data.token_count,
            "hit_count": data.hit_count,
            "enabled": data.enabled,
            "disabled_at": datetime_to_timestamp(data.disabled_at),
            "status": data.status,
            "error": data.error,
            "updated_at": datetime_to_timestamp(data.updated_at),
            "created_at": datetime_to_timestamp(data.created_at),
        }

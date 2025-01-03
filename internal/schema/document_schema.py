"""
@Time   : 2024/12/18 19:35
@Author : Leslie
@File   : document_schema.py
"""

import uuid
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from internal.entity import ProcessType, DEFAULT_PROCESS_RULE
from internal.schema import ListField, DictField
from internal.exception import ValidateErrorException
from wtforms.validators import DataRequired, AnyOf, Length, Optional
from internal.schema.schema import DictField
from marshmallow import Schema, fields, pre_dump
from internal.model import Document
from pkg.pagination import PaginationReq


class CreateDocumentsSchemaReq(FlaskForm):
    upload_file_ids = ListField("upload_file_ids")
    process_type = StringField(
        "process_type",
        validators=[
            DataRequired(message="process_type不能为空"),
            AnyOf(
                values=[ProcessType.AUTOMATIC, ProcessType.CUSTOM],
                message="process_type只能是automatic或custom",
            ),
        ],
    )
    rule = DictField("rule")

    def validate_upload_file_ids(self, field: ListField):
        if not isinstance(field.data, list):
            raise ValidateErrorException("文件id列表必须是数组")
        if len(field.data) == 0 or len(field.data) > 10:
            raise ValidateErrorException("文件id列表长度必须在1-10之间")
        for id in field.data:
            try:
                uuid.UUID(id)
            except Exception:
                raise ValidateErrorException("文件id格式错误")
        field.data = list(dict.fromkeys(field.data))

    def validate_rule(self, field: DictField):
        if self.process_type.data == ProcessType.AUTOMATIC:
            field.data = DEFAULT_PROCESS_RULE["rule"]
        else:
            if not isinstance(field.data, dict) or len(field.data) == 0:
                raise ValidateErrorException("rule必须是非空对象")
            if "pre_process_rules" not in field.data or not isinstance(
                field.data["pre_process_rules"], list
            ):
                raise ValidateErrorException("rule缺少pre_process_rules的列表字段")
            pre_process_rule_map = {}
            for pre_process_rule in field.data["pre_process_rules"]:
                if "id" not in pre_process_rule or pre_process_rule["id"] not in [
                    "remove_extra_space",
                    "remove_url_and_email",
                ]:
                    raise ValidateErrorException(
                        "pre_process_rules中的id字段只能是remove_extra_space或remove_url_and_email"
                    )

                if "enabled" not in pre_process_rule or not isinstance(
                    pre_process_rule["enabled"], bool
                ):
                    raise ValidateErrorException(
                        "pre_process_rules中的enabled字段必须是布尔值"
                    )

                pre_process_rule_map[pre_process_rule["id"]] = {
                    "id": pre_process_rule["id"],
                    "enabled": pre_process_rule["enabled"],
                }

            if len(pre_process_rule_map) != 2:
                raise ValidateErrorException(
                    "pre_process_rules中的id字段只能是remove_extra_space和remove_url_and_email"
                )

            field.data["pre_process_rules"] = list(pre_process_rule_map.values())

            if "segment" not in field.data or not isinstance(
                field.data["segment"], dict
            ):
                raise ValidateErrorException("rule缺少segment的对象字段")

            if "separators" not in field.data["segment"] or not isinstance(
                field.data["segment"]["separators"], list
            ):
                raise ValidateErrorException("segment缺少separators的列表字段")
            for seperator in field.data["segment"]["separators"]:
                if not isinstance(seperator, str):
                    raise ValidateErrorException("separators中的每个元素必须是字符串")
            if len(field.data["segment"]["separators"]) == 0:
                raise ValidateErrorException("separators不能为空")

            if "chunk_size" not in field.data["segment"] or not isinstance(
                field.data["segment"]["chunk_size"], int
            ):
                raise ValidateErrorException("segment缺少chunk_size的整数字段")

            if (
                field.data["segment"]["chunk_size"] < 100
                or field.data["segment"]["chunk_size"] > 1000
            ):
                raise ValidateErrorException("chunk_size必须在100-1000之间")

            if "chunk_overlap" not in field.data["segment"] or not isinstance(
                field.data["segment"]["chunk_overlap"], int
            ):
                raise ValidateErrorException("segment缺少chunk_overlap的整数字段")
            if not (
                0
                <= field.data["segment"]["chunk_overlap"]
                <= field.data["segment"]["chunk_size"] * 0.5
            ):
                raise ValidateErrorException(
                    f"块重叠大小在0-{int(field.data['segment']['chunk_size'] * 0.5)}"
                )

            field.data = {
                "pre_process_rules": field.data["pre_process_rules"],
                "segment": {
                    "separators": field.data["segment"]["separators"],
                    "chunk_size": field.data["segment"]["chunk_size"],
                    "chunk_overlap": field.data["segment"]["chunk_overlap"],
                },
            }


class CreateDocumentsSchemaRes(Schema):
    documents = fields.List(fields.Dict(), dump_default=[])
    batch = fields.String(dump_default="")

    @pre_dump
    def process_data(self, data: tuple[list[Document], str], **kwargs):
        return {
            "documents": [
                {
                    "id": doc.id,
                    "name": doc.name,
                    "status": doc.status,
                    "created_at": int(doc.created_at.timestamp()),
                }
                for doc in data[0]
            ],
            "batch": data[1],
        }


class GetDocumentSchemaRes(Schema):
    id = fields.UUID()
    dataset_id = fields.UUID()
    name = fields.String()
    segment_count = fields.Integer()
    character_count = fields.Integer()
    hit_count = fields.Integer()
    position = fields.Integer()
    enabled = fields.Boolean()
    disabled_at = fields.Integer()
    status = fields.String()
    error = fields.String()
    updated_at = fields.Integer()
    created_at = fields.Integer()


class UpdateDocumentNameSchemaReq(FlaskForm):
    name = StringField(
        "name",
        validators=[
            DataRequired(message="name不能为空"),
            Length(min=1, max=100, message="name长度必须在1-100之间"),
        ],
    )


class GetDocumentsPaginationSchemaReq(PaginationReq):
    search_word = StringField(
        "search_word",
        validators=[
            Optional(),
        ],
    )


class GetDocumentsPaginationItemSchemaRes(Schema):
    id = fields.UUID()
    name = fields.String()
    character_count = fields.Integer()
    hit_count = fields.Integer()
    position = fields.Integer()
    enabled = fields.Boolean()
    disabled_at = fields.Integer()
    status = fields.String()
    error = fields.String()
    updated_at = fields.Integer()
    created_at = fields.Integer()


class UpdateDocumentEnabledSchemaReq(FlaskForm):
    enabled = BooleanField("enabled")

    def validate_enabled(self, field: BooleanField):
        if not isinstance(field.data, bool):
            raise ValidateErrorException("enabled字段必须是布尔值")

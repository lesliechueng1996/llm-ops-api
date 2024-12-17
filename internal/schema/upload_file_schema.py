"""
@Time   : 2024/12/17 14:19
@Author : Leslie
@File   : upload_file_schema.py
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileSize, FileAllowed, FileRequired
from internal.entity import ALLOWED_DOCUMENT_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS
from marshmallow import Schema, fields, pre_dump
from internal.model import UploadFile


class UploadFileSchemaReq(FlaskForm):
    file = FileField(
        "file",
        validators=[
            FileRequired(message="文件不能为空"),
            FileSize(max_size=15 * 1024 * 1024, message="文件大小不能超过15MB"),
            FileAllowed(
                ALLOWED_DOCUMENT_EXTENSIONS,
                message=f"仅支持上传{'/'.join(ALLOWED_DOCUMENT_EXTENSIONS)}格式的文件",
            ),
        ],
    )


class UploadFileSchemaRes(Schema):
    id = fields.UUID()
    account_id = fields.UUID()
    name = fields.String()
    key = fields.String()
    size = fields.Integer()
    extension = fields.String()
    mime_type = fields.String()
    created_at = fields.Integer()

    @pre_dump
    def proces_data(self, data: UploadFile, **kwargs):
        return {
            "id": data.id,
            "account_id": data.account_id,
            "name": data.name,
            "key": data.key,
            "size": data.size,
            "extension": data.extension,
            "mime_type": data.mime_type,
            "created_at": int(data.created_at.timestamp()),
        }


class UploadImageSchemaReq(FlaskForm):
    file = FileField(
        "file",
        validators=[
            FileRequired(message="图片不能为空"),
            FileSize(max_size=15 * 1024 * 1024, message="图片大小不能超过15MB"),
            FileAllowed(
                ALLOWED_IMAGE_EXTENSIONS,
                message=f"仅支持上传{'/'.join(ALLOWED_IMAGE_EXTENSIONS)}格式的图片",
            ),
        ],
    )

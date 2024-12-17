"""
@Time   : 2024/12/17 14:18
@Author : Leslie
@File   : upload_file_handler.py
"""

from injector import inject
from dataclasses import dataclass
from internal.schema import UploadFileSchemaReq, UploadImageSchemaReq
from internal.service import UploadFileService
from pkg.response import validate_error_json, success_message, success_json


@inject
@dataclass
class UploadFileHandler:
    upload_file_service: UploadFileService

    def upload_file(self):
        req = UploadFileSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.upload_file_service.upload_file(req.file.data)
        return success_message("上传文件成功")

    def upload_image(self):
        req = UploadImageSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        url = self.upload_file_service.upload_image(req.file.data)
        return success_json({"image_url": url})

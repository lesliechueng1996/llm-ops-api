"""
@Time   : 2024/12/17 14:18
@Author : Leslie
@File   : upload_file_handler.py
"""

from injector import inject
from dataclasses import dataclass
from internal.schema import UploadFileSchemaReq
from internal.service import UploadFileService
from pkg.response import validate_error_json, success_message


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

"""
@Time   : 2024/12/17 14:18
@Author : Leslie
@File   : upload_file_handler.py
"""

from injector import inject
from dataclasses import dataclass
from internal.schema import (
    UploadFileSchemaReq,
    UploadImageSchemaReq,
    UploadFileSchemaRes,
)
from internal.service import UploadFileService
from pkg.response import validate_error_json, success_json
from flask_login import login_required, current_user


@inject
@dataclass
class UploadFileHandler:
    upload_file_service: UploadFileService

    @login_required
    def upload_file(self):
        req = UploadFileSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        upload_file = self.upload_file_service.upload_file(req.file.data, current_user)
        schema = UploadFileSchemaRes()
        return success_json(schema.dump(upload_file))

    @login_required
    def upload_image(self):
        req = UploadImageSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        url = self.upload_file_service.upload_image(req.file.data)
        return success_json({"image_url": url})

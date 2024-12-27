"""
@Time   : 2024/12/17 15:07
@Author : Leslie
@File   : upload_file_service.py
"""

from injector import inject
from dataclasses import dataclass
from werkzeug.datastructures import FileStorage
from internal.model import UploadFile
from internal.service.cos_service import CosService
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class UploadFileService:
    cosService: CosService
    db: SQLAlchemy

    def upload_file(self, file: FileStorage):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        result = self.cosService.upload_file(file)
        with self.db.auto_commit():
            upload_file = UploadFile(account_id=account_id, **result)
            self.db.session.add(upload_file)

        return upload_file

    def upload_image(self, file: FileStorage):
        result = self.cosService.upload_file(file, only_image=True)
        return self.cosService.get_file_url(result["key"])

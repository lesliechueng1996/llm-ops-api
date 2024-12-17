"""
@Time   : 2024/12/18 01:08
@Author : Leslie
@File   : dataset_handler.py
"""

from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.schema import CreateDatasetSchemaReq, UpdateDatasetSchemaReq
from internal.service import DatasetService
from pkg.response import validate_error_json, success_message


@inject
@dataclass
class DatasetHandler:

    dataset_service: DatasetService

    def create_dataset(self):
        req = CreateDatasetSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.dataset_service.create_dataset(req)
        return success_message("创建知识库成功")

    def update_dataset(self, dataset_id: UUID):
        req = UpdateDatasetSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.dataset_service.update_dataset(dataset_id, req)
        return success_message("更新知识库成功")

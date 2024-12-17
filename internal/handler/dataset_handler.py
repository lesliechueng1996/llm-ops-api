"""
@Time   : 2024/12/18 01:08
@Author : Leslie
@File   : dataset_handler.py
"""

from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.schema import (
    CreateDatasetSchemaReq,
    UpdateDatasetSchemaReq,
    GetDatasetSchemaRes,
    GetDatasetsPaginationSchemaReq,
    GetDatasetsPaginationItemSchemaRes,
)
from internal.service import DatasetService
from pkg.pagination import PageModel
from pkg.response import validate_error_json, success_message, success_json
from flask import request


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

    def get_dataset(self, dataset_id: UUID):
        dataset = self.dataset_service.get_dataset(dataset_id)
        schema = GetDatasetSchemaRes()

        return success_json(schema.dump(dataset))

    def get_datasets_pagination(self):
        req = GetDatasetsPaginationSchemaReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)
        datasets, paginator = self.dataset_service.get_datasets_pagination(req)
        schema = GetDatasetsPaginationItemSchemaRes(many=True)

        dump_list = schema.dump(datasets)
        return success_json(PageModel(dump_list, paginator))

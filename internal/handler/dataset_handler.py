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
    HitDatasetSchemaReq,
    GetDatasetQueriesSchemaRes,
)
from internal.service import DatasetService
from pkg.pagination import PageModel
from pkg.response import validate_error_json, success_message, success_json
from flask import request
from flask_login import login_required, current_user


@inject
@dataclass
class DatasetHandler:

    dataset_service: DatasetService

    @login_required
    def create_dataset(self):
        req = CreateDatasetSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.dataset_service.create_dataset(req, current_user)
        return success_message("创建知识库成功")

    @login_required
    def update_dataset(self, dataset_id: UUID):
        req = UpdateDatasetSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)
        self.dataset_service.update_dataset(dataset_id, req, current_user)
        return success_message("更新知识库成功")

    @login_required
    def get_dataset(self, dataset_id: UUID):
        dataset = self.dataset_service.get_dataset(dataset_id, current_user)
        schema = GetDatasetSchemaRes()

        return success_json(schema.dump(dataset))

    @login_required
    def get_datasets_pagination(self):
        req = GetDatasetsPaginationSchemaReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)
        datasets, paginator = self.dataset_service.get_datasets_pagination(
            req, current_user
        )
        schema = GetDatasetsPaginationItemSchemaRes(many=True)

        dump_list = schema.dump(datasets)
        return success_json(PageModel(dump_list, paginator))

    @login_required
    def hit_dataset(self, dataset_id: UUID):
        req = HitDatasetSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)

        result = self.dataset_service.hit_dataset(dataset_id, req, current_user)
        return success_json(result)

    @login_required
    def get_dataset_queries(self, dataset_id: UUID):
        dataset_queries = self.dataset_service.get_dataset_queries(
            dataset_id, current_user
        )
        schema = GetDatasetQueriesSchemaRes(many=True)
        return success_json(schema.dump(dataset_queries))

    @login_required
    def delete_dataset(self, dataset_id: UUID):
        self.dataset_service.delete_dataset(dataset_id, current_user)
        return success_message("删除知识库成功")

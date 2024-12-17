"""
@Time   : 2024/12/18 01:18
@Author : Leslie
@File   : dataset_service.py
"""

from injector import inject
from dataclasses import dataclass
from internal.schema import CreateDatasetSchemaReq, UpdateDatasetSchemaReq
from pkg.sqlalchemy import SQLAlchemy
from internal.model import Dataset
from internal.entity import DEFAULT_DATASET_DESCRIPTION_FORMATTER
from internal.exception import ValidateErrorException, NotFoundException


@inject
@dataclass
class DatasetService:
    db: SQLAlchemy

    def create_dataset(self, req: CreateDatasetSchemaReq):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        same_name_record = (
            self.db.session.query(Dataset)
            .filter_by(account_id=account_id, name=req.name.data)
            .one_or_none()
        )
        if same_name_record:
            raise ValidateErrorException(f"知识库名称 {req.name.data} 已存在")

        description = req.description.data
        if not description:
            description = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(
                name=req.name.data
            )

        with self.db.auto_commit():
            dataset = Dataset(
                account_id=account_id,
                name=req.name.data,
                description=description,
                icon=req.icon.data,
            )
            self.db.session.add(dataset)

    def update_dataset(self, dataset_id: str, req: UpdateDatasetSchemaReq):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        dataset = self.db.session.query(Dataset).get(dataset_id)
        if not dataset:
            raise NotFoundException("知识库不存在")

        same_name_record = (
            self.db.session.query(Dataset)
            .filter(
                Dataset.account_id == account_id,
                Dataset.name == req.name.data,
                Dataset.id != dataset_id,
            )
            .one_or_none()
        )

        if same_name_record:
            raise ValidateErrorException(f"知识库名称 {req.name.data} 已存在")

        description = req.description.data
        if not description:
            description = DEFAULT_DATASET_DESCRIPTION_FORMATTER.format(
                name=req.name.data
            )

        with self.db.auto_commit():
            dataset.name = req.name.data
            dataset.description = description
            dataset.icon = req.icon.data

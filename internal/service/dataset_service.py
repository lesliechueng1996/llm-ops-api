"""
@Time   : 2024/12/18 01:18
@Author : Leslie
@File   : dataset_service.py
"""

from injector import inject
from dataclasses import dataclass
from internal.schema import CreateDatasetSchemaReq, UpdateDatasetSchemaReq
from pkg.sqlalchemy import SQLAlchemy
from internal.model import Dataset, Document, Segment, AppDatasetJoin
from internal.entity import DEFAULT_DATASET_DESCRIPTION_FORMATTER
from internal.exception import ValidateErrorException, NotFoundException
from sqlalchemy import func


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

    def get_dataset(self, dataset_id: str) -> dict:
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        dataset = self.db.session.query(Dataset).get(dataset_id)
        if not dataset or str(dataset.account_id) != account_id:
            raise NotFoundException("知识库不存在")

        document_result = (
            self.db.session.query(
                func.count(Document.id),
                func.coalesce(func.sum(Document.character_count), 0),
            )
            .filter(Document.dataset_id == dataset_id)
            .one()
        )

        hit_count = (
            self.db.session.query(func.coalesce(func.sum(Segment.hit_count), 0))
            .filter(Segment.dataset_id == dataset_id)
            .scalar()
        )

        related_app_count = (
            self.db.session.query(func.count(AppDatasetJoin.id))
            .filter(AppDatasetJoin.dataset_id == dataset_id)
            .scalar()
        )
        return {
            "id": dataset.id,
            "name": dataset.name,
            "icon": dataset.icon,
            "description": dataset.description,
            "document_count": document_result[0],
            "hit_count": hit_count,
            "related_app_count": related_app_count,
            "character_count": document_result[1],
            "updated_at": dataset.updated_at,
            "created_at": dataset.created_at,
        }

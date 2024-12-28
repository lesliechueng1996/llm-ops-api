"""
@Time   : 2024/12/18 01:18
@Author : Leslie
@File   : dataset_service.py
"""

import logging
from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.model.account import Account
from internal.schema import (
    CreateDatasetSchemaReq,
    UpdateDatasetSchemaReq,
    GetDatasetsPaginationSchemaReq,
    HitDatasetSchemaReq,
)
from internal.service.retrieval_service import RetrievalService
from pkg.sqlalchemy import SQLAlchemy
from internal.model import (
    Dataset,
    Document,
    Segment,
    AppDatasetJoin,
    UploadFile,
    DatasetQuery,
)
from internal.entity import DEFAULT_DATASET_DESCRIPTION_FORMATTER, RetrievalSource
from internal.exception import ValidateErrorException, NotFoundException, FailException
from sqlalchemy import func, desc
from pkg.pagination import Paginator
from internal.lib.helper import datetime_to_timestamp
from internal.task.dataset_task import delete_dataset


@inject
@dataclass
class DatasetService:
    db: SQLAlchemy
    retrieval_service: RetrievalService

    def create_dataset(self, req: CreateDatasetSchemaReq, account: Account):
        account_id = str(account.id)

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

    def update_dataset(
        self, dataset_id: str, req: UpdateDatasetSchemaReq, account: Account
    ):
        account_id = str(account.id)

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

    def get_dataset(self, dataset_id: str, account: Account) -> dict:
        account_id = str(account.id)

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

    def get_datasets_pagination(
        self, req: GetDatasetsPaginationSchemaReq, account: Account
    ) -> list:
        account_id = str(account.id)

        filters = [Dataset.account_id == account_id]
        if req.search_word.data:
            filters.append(Dataset.name.ilike(f"%{req.search_word.data}%"))

        paginator = Paginator(self.db, req)

        datasets = paginator.paginate(
            self.db.session.query(Dataset).filter(*filters).order_by(desc("created_at"))
        )

        dataset_ids = [dataset.id for dataset in datasets]
        document_result = (
            self.db.session.query(
                Document.dataset_id,
                func.count(Document.id),
                func.coalesce(func.sum(Document.character_count), 0),
            )
            .filter(Document.dataset_id.in_(dataset_ids))
            .group_by(Document.dataset_id)
            .all()
        )
        document_map = {item[0]: item for item in document_result}

        app_result = (
            self.db.session.query(
                AppDatasetJoin.dataset_id, func.count(AppDatasetJoin.id)
            )
            .filter(AppDatasetJoin.dataset_id.in_(dataset_ids))
            .group_by(AppDatasetJoin.dataset_id)
            .all()
        )
        app_map = {item[0]: item for item in app_result}

        return [
            {
                "id": dataset.id,
                "name": dataset.name,
                "icon": dataset.icon,
                "description": dataset.description,
                "document_count": document_map.get(dataset.id, (0, 0, 0))[1],
                "character_count": document_map.get(dataset.id, (0, 0, 0))[2],
                "related_app_count": app_map.get(dataset.id, 0),
                "updated_at": dataset.updated_at,
                "created_at": dataset.created_at,
            }
            for dataset in datasets
        ], paginator

    def hit_dataset(self, dataset_id: UUID, req: HitDatasetSchemaReq, account: Account):
        account_id = str(account.id)

        dataset = (
            self.db.session.query(Dataset)
            .filter(Dataset.account_id == account_id, Dataset.id == dataset_id)
            .one_or_none()
        )
        if not dataset:
            raise NotFoundException("知识库不存在")

        lc_docs = self.retrieval_service.search_in_databases(
            account_id=account_id,
            dataset_ids=[dataset_id],
            query=req.query.data,
            retrieval_strategy=req.retrieval_strategy.data,
            k=req.k.data,
            score=req.score.data,
            retrival_source=RetrievalSource.HIT_TESTING,
        )
        segment_lc_doc_map = {
            str(lc_doc.metadata["segment_id"]): lc_doc for lc_doc in lc_docs
        }

        segment_ids = [str(lc_doc.metadata["segment_id"]) for lc_doc in lc_docs]
        segments = (
            self.db.session.query(Segment).filter(Segment.id.in_(segment_ids)).all()
        )

        document_ids = [segment.document_id for segment in segments]
        documents = (
            self.db.session.query(Document).filter(Document.id.in_(document_ids)).all()
        )
        document_map = {str(document.id): document for document in documents}

        upload_file_ids = [document.upload_file_id for document in documents]
        upload_files = (
            self.db.session.query(UploadFile)
            .filter(UploadFile.id.in_(upload_file_ids))
            .all()
        )
        upload_file_map = {
            str(upload_file.id): upload_file for upload_file in upload_files
        }

        results = []

        for segment in segments:
            document = document_map[str(segment.document_id)]
            upload_file = upload_file_map[str(document.upload_file_id)]

            result = {
                "id": segment.id,
                "document": {
                    "id": document.id,
                    "name": document.name,
                    "extension": upload_file.extension,
                    "mime_type": upload_file.mime_type,
                },
                "dataset_id": segment.dataset_id,
                "score": segment_lc_doc_map[str(segment.id)].metadata["score"],
                "position": segment.position,
                "content": segment.content,
                "keywords": segment.keywords,
                "character_count": segment.character_count,
                "token_count": segment.token_count,
                "hit_count": segment.hit_count,
                "enabled": segment.enabled,
                "disabled_at": datetime_to_timestamp(segment.disabled_at),
                "status": segment.status,
                "error": segment.error,
                "updated_at": datetime_to_timestamp(segment.updated_at),
                "created_at": datetime_to_timestamp(segment.created_at),
            }
            results.append(result)

        return results

    def get_dataset_queries(self, dataset_id: UUID, account: Account):
        account_id = str(account.id)

        dataset = (
            self.db.session.query(Dataset)
            .filter(Dataset.id == dataset_id, Dataset.account_id == account_id)
            .one_or_none()
        )
        if not dataset:
            raise NotFoundException("知识库不存在")

        return (
            self.db.session.query(DatasetQuery)
            .filter(DatasetQuery.dataset_id == dataset_id)
            .order_by(desc(DatasetQuery.created_at))
            .limit(10)
            .all()
        )

    def delete_dataset(self, dataset_id: UUID, account: Account):
        account_id = str(account.id)

        dataset = (
            self.db.session.query(Dataset)
            .filter(Dataset.id == dataset_id, Dataset.account_id == account_id)
            .one_or_none()
        )
        if not dataset:
            raise NotFoundException("知识库不存在")

        try:
            with self.db.auto_commit():
                self.db.session.delete(dataset)

                self.db.session.query(AppDatasetJoin).filter(
                    AppDatasetJoin.dataset_id == dataset_id
                ).delete()

                delete_dataset.delay(dataset_id)
        except Exception as e:
            logging.exception(
                f"删除知识库失败, dataset_id: {dataset_id}, 错误信息: {str(e)}"
            )
            raise FailException("删除知识库失败，请稍后重试")

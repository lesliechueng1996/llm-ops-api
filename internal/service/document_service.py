"""
@Time   : 2024/12/18 20:26
@Author : Leslie
@File   : document_service.py
"""

import logging
from uuid import UUID
from injector import inject
from dataclasses import dataclass
from pkg.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from internal.task.document_task import build_documents
from internal.model import Document, Dataset, UploadFile, ProcessRule, Segment
from internal.exception import NotFoundException, FailException
from internal.entity import ALLOWED_DOCUMENT_EXTENSIONS, ProcessType, SegmentStatus
import time
import random
from internal.lib.helper import datetime_to_timestamp


@inject
@dataclass
class DocumentService:
    db: SQLAlchemy

    def create_documents(
        self,
        dataset_id: str,
        upload_file_ids: list[str],
        process_type: str = ProcessType.AUTOMATIC,
        rule: dict = {},
    ) -> tuple[list[Document], str]:
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        # 校验数据集是否存在
        dataset = (
            self.db.session.query(Dataset)
            .filter(Dataset.id == dataset_id, Dataset.account_id == account_id)
            .one_or_none()
        )
        if not dataset:
            raise NotFoundException("数据集不存在")

        # 校验上传文件
        upload_files = (
            self.db.session.query(UploadFile)
            .filter(
                UploadFile.account_id == account_id,
                UploadFile.id.in_(upload_file_ids),
            )
            .all()
        )

        allowed_upload_files = [
            file
            for file in upload_files
            if file.extension.lower() in ALLOWED_DOCUMENT_EXTENSIONS
        ]
        if len(allowed_upload_files) == 0:
            logging.warning(
                f"上传文档列表未解析到合法文件，account_id: {account_id}, dataset_id: {dataset_id}, upload_file_ids: {upload_file_ids}"
            )
            raise FailException("暂未解析到合法文件，请重新上传")

        # 创建批次
        with self.db.auto_commit():
            batch = time.strftime("%Y%m%d%H%M%S") + str(random.randint(100000, 999999))
            process_rule = ProcessRule(
                account_id=account_id,
                dataset_id=dataset_id,
                mode=process_type,
                rule=rule,
            )
            self.db.session.add(process_rule)
            self.db.session.flush()

            start_position = self.get_latest_document_position(dataset_id=dataset_id)

            documents = []
            for upload_file in allowed_upload_files:
                start_position += 1
                document = Document(
                    account_id=account_id,
                    dataset_id=dataset_id,
                    upload_file_id=upload_file.id,
                    process_rule_id=process_rule.id,
                    batch=batch,
                    name=upload_file.name,
                    position=start_position,
                )
                documents.append(document)

            self.db.session.add_all(documents)

        # 触发构建文档任务
        build_documents.delay([document.id for document in documents])

        return documents, batch

    def get_latest_document_position(self, dataset_id: str) -> int:
        last_document = (
            self.db.session.query(Document)
            .filter(Document.dataset_id == dataset_id)
            .order_by(Document.position.desc())
            .first()
        )
        return last_document.position if last_document else 0

    def get_documents_batch_status(self, dataset_id: UUID, batch: str) -> list[dict]:
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        docs = (
            self.db.session.query(Document)
            .filter(
                Document.account_id == account_id,
                Document.dataset_id == dataset_id,
                Document.batch == batch,
            )
            .all()
        )
        if docs is None or len(docs) == 0:
            raise NotFoundException("未发现该批次文档，请稍后再试")

        doc_status_list = []
        for doc in docs:
            upload_file = (
                self.db.session.query(UploadFile)
                .filter(UploadFile.id == doc.upload_file_id)
                .one_or_none()
            )
            if upload_file is None:
                continue

            segment_count = (
                self.db.session.query(func.count(Segment.id))
                .filter(Segment.document_id == doc.id)
                .scalar()
            )
            completed_segment_count = (
                self.db.session.query(func.count(Segment.id))
                .filter(
                    Segment.document_id == doc.id,
                    Segment.status == SegmentStatus.COMPLETED,
                )
                .scalar()
            )

            doc_status = {
                "id": doc.id,
                "name": doc.name,
                "size": upload_file.size,
                "extension": upload_file.extension,
                "mime_type": upload_file.mime_type,
                "position": doc.position,
                "segment_count": segment_count,
                "completed_segment_count": completed_segment_count,
                "error": doc.error,
                "status": doc.status,
                "processing_started_at": datetime_to_timestamp(
                    doc.processing_started_at
                ),
                "parsing_completed_at": datetime_to_timestamp(doc.parsing_completed_at),
                "splitting_completed_at": datetime_to_timestamp(
                    doc.splitting_completed_at
                ),
                "indexing_completed_at": datetime_to_timestamp(
                    doc.indexing_completed_at
                ),
                "completed_at": datetime_to_timestamp(doc.completed_at),
                "stopped_at": datetime_to_timestamp(doc.stopped_at),
                "created_at": datetime_to_timestamp(doc.created_at),
            }
            doc_status_list.append(doc_status)
        return doc_status_list

    def get_document(self, dataset_id: UUID, document_id: UUID) -> dict:
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        doc = (
            self.db.session.query(Document)
            .filter(
                Document.account_id == account_id,
                Document.dataset_id == dataset_id,
                Document.id == document_id,
            )
            .one_or_none()
        )

        if doc is None:
            raise NotFoundException("文档不存在")

        segment_count = (
            self.db.session.query(func.count(Segment.id))
            .filter(Segment.document_id == doc.id)
            .scalar()
        )
        hit_count = (
            self.db.session.query(
                func.coalesce(
                    func.sum(Segment.hit_count),
                )
            )
            .filter(Segment.document_id == doc.id)
            .scalar()
        )

        return {
            "id": doc.id,
            "dataset_id": doc.dataset_id,
            "name": doc.name,
            "segment_count": segment_count,
            "character_count": doc.character_count,
            "hit_count": hit_count,
            "position": doc.position,
            "enabled": doc.enabled,
            "disabled_at": datetime_to_timestamp(doc.disabled_at),
            "status": doc.status,
            "error": doc.error,
            "updated_at": datetime_to_timestamp(doc.updated_at),
            "created_at": datetime_to_timestamp(doc.created_at),
        }

    def update_document_name(self, dataset_id: UUID, document_id: UUID, name: str):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        doc = (
            self.db.session.query(Document)
            .filter(
                Document.account_id == account_id,
                Document.dataset_id == dataset_id,
                Document.id == document_id,
            )
            .one_or_none()
        )

        if doc is None:
            raise NotFoundException("文档不存在")

        with self.db.auto_commit():
            doc.name = name
        return

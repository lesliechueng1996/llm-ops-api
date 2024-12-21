"""
@Time   : 2024/12/21 17:40
@Author : Leslie
@File   : segment_service.py
"""

from datetime import datetime
from flask import logging
from injector import inject
from dataclasses import dataclass
from internal.lib.helper import generate_text_hash
from redis import Redis
from internal.entity import LOCK_SEGMENT_UPDATE_ENABLED
from pkg.sqlalchemy import SQLAlchemy
from internal.schema import GetSegmentsPaginationSchemaReq, CreateSegmentSchemaReq
from pkg.pagination import Paginator
from internal.model import Segment, Document
from sqlalchemy import asc
from internal.exception import NotFoundException, FailException, ValidateErrorException
from internal.entity import SegmentStatus, DocumentStatus
from internal.lib.redis_lock import release_lock, acquire_lock
from uuid import uuid4
from .vector_store_service import VectorStoreService
from .keyword_table_service import KeywordTableService
from .jieba_service import JiebaService
from .embedding_service import EmbeddingService
from sqlalchemy import func
from langchain_core.documents import Document as LangchainDocument


@inject
@dataclass
class SegmentService:
    db: SQLAlchemy
    redis_client: Redis
    vector_store_service: VectorStoreService
    keyword_table_service: KeywordTableService
    jieba_service: JiebaService
    embedding_service: EmbeddingService

    def get_segments_pagination(
        self, dataset_id: str, document_id: str, req: GetSegmentsPaginationSchemaReq
    ):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        paginator = Paginator(self.db, req)

        filter = [
            Segment.dataset_id == dataset_id,
            Segment.document_id == document_id,
            Segment.account_id == account_id,
        ]

        if req.search_word.data:
            filter.append(Segment.content.ilike(f"%{req.search_word.data}%"))

        segments = paginator.paginate(
            self.db.session.query(Segment)
            .filter(*filter)
            .order_by(asc(Segment.position))
        )

        return segments, paginator

    def get_segment(self, dataset_id: str, document_id: str, segment_id: str):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        segment = (
            self.db.session.query(Segment)
            .filter(
                Segment.dataset_id == dataset_id,
                Segment.document_id == document_id,
                Segment.account_id == account_id,
                Segment.id == segment_id,
            )
            .one_or_none()
        )

        if not segment:
            raise NotFoundException("该片段不存在")

        return segment

    def update_segment_enabled(
        self, dataset_id: str, document_id: str, segment_id: str, enabled: bool
    ):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        segment = (
            self.db.session.query(Segment)
            .filter(
                Segment.dataset_id == dataset_id,
                Segment.document_id == document_id,
                Segment.account_id == account_id,
                Segment.id == segment_id,
            )
            .one_or_none()
        )

        if not segment:
            raise NotFoundException("该片段不存在")

        if segment.status != SegmentStatus.COMPLETED:
            raise FailException("该片段未完成, 暂时无法修改")

        if segment.enabled == enabled:
            raise FailException(
                f"片段状态修改错误，当前已是{'启用' if enabled else '禁用'}"
            )

        lock_key = LOCK_SEGMENT_UPDATE_ENABLED.format(segment_id=segment.id)
        lock_value = str(uuid4())
        if not acquire_lock(self.redis_client, lock_key, lock_value):
            raise FailException("当前文档片段正在修改状态，请稍后尝试")

        try:
            document = (
                self.db.session.query(Document)
                .filter(Document.id == document_id)
                .one_or_none()
            )
            if not document:
                raise NotFoundException("所属文档不存在")

            with self.db.auto_commit():
                segment.enabled = enabled
                segment.disabled_at = None if enabled else datetime.now()

            self.vector_store_service.collection.data.update(
                uuid=segment.node_id,
                properties={"segment_enabled": enabled},
            )

            if enabled is True and document.enabled is True:
                self.keyword_table_service.add_keyword_table_from_ids(
                    dataset_id, [segment_id]
                )
            else:
                self.keyword_table_service.delete_keyword_table_from_ids(
                    dataset_id, [segment_id]
                )
        except Exception as e:
            logging.error(
                f"更改文档片段启用状态出现异常, segment_id: {segment_id}, 错误信息: {str(e)}"
            )

            with self.db.auto_commit():
                segment.enabled = False
                segment.disabled_at = datetime.now()
                segment.error = str(e)
                segment.status = SegmentStatus.ERROR
                segment.stopped_at = datetime.now()

            raise FailException("更改文档片段启用状态失败")
        finally:
            release_lock(self.redis_client, lock_key, lock_value)

    def create_segment(
        self, dataset_id: str, document_id: str, req: CreateSegmentSchemaReq
    ):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"

        token = self.embedding_service.calculate_token_count(req.content.data)
        if token > 1000:
            raise ValidateErrorException("片段内容的长度不能超过1000 token")

        document = (
            self.db.session.query(Document)
            .filter(
                Document.id == document_id,
                Document.account_id == account_id,
                Document.dataset_id == dataset_id,
            )
            .one_or_none()
        )
        if not document:
            raise NotFoundException("所属文档不存在")

        if document.status != DocumentStatus.COMPLETED:
            raise FailException("所属文档未完成，暂时无法添加片段")

        position = (
            self.db.session.query(func.coalesce(func.max(Segment.position), 0))
            .filter(Segment.document_id == document_id)
            .scalar()
        )

        if req.keywords.data is None or len(req.keywords.data) == 0:
            req.keywords.data = self.jieba_service.extract_keywords(
                req.content.data, 10
            )

        segment = None
        try:
            with self.db.auto_commit():
                now = datetime.now()
                segment = Segment(
                    account_id=account_id,
                    dataset_id=dataset_id,
                    document_id=document_id,
                    node_id=uuid4(),
                    position=position + 1,
                    content=req.content.data,
                    character_count=len(req.content.data),
                    token_count=token,
                    keywords=req.keywords.data,
                    hash=generate_text_hash(req.content.data),
                    enabled=True,
                    processing_started_at=now,
                    indexing_completed_at=now,
                    completed_at=now,
                    status=SegmentStatus.COMPLETED,
                )
                self.db.session.add(segment)

            self.vector_store_service.vector_store.add_documents(
                [
                    LangchainDocument(
                        page_content=req.content.data,
                        metadata={
                            "account_id": str(account_id),
                            "dataset_id": str(dataset_id),
                            "document_id": str(document_id),
                            "segment_id": str(segment.id),
                            "node_id": str(segment.node_id),
                            "document_enabled": document.enabled,
                            "segment_enabled": True,
                        },
                    )
                ],
                ids=[str(segment.node_id)],
            )

            document_character_count, document_token_count = (
                self.db.session.query(
                    func.coalesce(func.sum(Segment.character_count), 0),
                    func.coalesce(func.sum(Segment.token_count), 0),
                )
                .filter(Segment.document_id == document_id)
                .first()
            )

            with self.db.auto_commit():
                document.character_count = document_character_count
                document.token_count = document_token_count

            if document.enabled is True:
                self.keyword_table_service.add_keyword_table_from_ids(
                    dataset_id, [segment.id]
                )

        except Exception as e:
            logging.exception(f"新增文档片段内容发生异常, 错误信息: {str(e)}")
            if segment:
                with self.db.auto_commit():
                    segment.status = SegmentStatus.ERROR
                    segment.error = str(e)
                    segment.enabled = False
                    segment.disabled_at = datetime.now()
                    segment.stopped_at = datetime.now()
            raise FailException("新增文档片段内容失败")

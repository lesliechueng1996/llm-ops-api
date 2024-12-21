"""
@Time   : 2024/12/19 02:29
@Author : Leslie
@File   : indexing_service.py
"""

from concurrent.futures import ThreadPoolExecutor
import logging
import re
from uuid import UUID, uuid4
from flask import Flask, current_app
from injector import inject
from dataclasses import dataclass
from redis import Redis
from sqlalchemy import func
from internal.lib.redis_lock import release_lock
from pkg.sqlalchemy import SQLAlchemy
from internal.model import Document, UploadFile, ProcessRule, Segment, KeywordTable
from internal.lib import generate_text_hash
from internal.entity import DocumentStatus, SegmentStatus
from datetime import datetime
from internal.core.file_extractor import FileExtractor
from internal.service import (
    EmbeddingService,
    JiebaService,
    VectorStoreService,
)
from internal.service.keyword_table_service import KeywordTableService
from internal.service.process_rule_service import ProcessRuleService
from langchain_core.documents import Document as LangchainDocument
from weaviate.classes.query import Filter


@inject
@dataclass
class IndexingService:
    db: SQLAlchemy
    file_extractor: FileExtractor
    process_rule_service: ProcessRuleService
    embedding_service: EmbeddingService
    jieba_service: JiebaService
    keyword_table_service: KeywordTableService
    vector_store_service: VectorStoreService
    redis_client: Redis

    def build_documents(self, document_ids: list[UUID]):
        if not document_ids or len(document_ids) == 0:
            return

        # 获取所有文档
        logging.info(f"Start build documents {document_ids}")
        documents = (
            self.db.session.query(Document).filter(Document.id.in_(document_ids)).all()
        )

        keyword_table_record = (
            self.keyword_table_service.get_keyword_table_from_dataset_id(
                dataset_id=documents[0].dataset_id
            )
        )

        for document in documents:
            try:
                # 更新文档状态解析中
                logging.info(f"Update document {document.id} status to parsing")
                with self.db.auto_commit():
                    document.status = DocumentStatus.PARSING
                    document.processing_started_at = datetime.now()

                # 加载文档，更新状态为解析完成
                langchain_docs = self._parseing(document)

                # 分割文档，更新状态为分割完成
                langchain_segments = self._splitting(document, langchain_docs)

                # 索引文档，更新状态为索引完成
                self._indexing(document, langchain_segments, keyword_table_record)

                # 完成文档，更新状态为完成
                self._completed(document, langchain_segments)

            except Exception as e:
                logging.error(f"Build document {document.id} failed, {e}")
                with self.db.auto_commit():
                    document.status = DocumentStatus.ERROR
                    document.error = str(e)
                    document.stopped_at = datetime.now()
        pass

    def _parseing(self, document: Document):
        logging.info(f"Start parsing document {document.id}")
        upload_file = self.db.session.query(UploadFile).get(document.upload_file_id)
        langchain_docs = self.file_extractor.load(
            upload_file=upload_file, return_text=False, is_unstructured=True
        )

        character_count = 0
        for langchain_doc in langchain_docs:
            langchain_doc.page_content = self._clean_extra_text(
                langchain_doc.page_content
            )
            character_count += len(langchain_doc.page_content)

        with self.db.auto_commit():
            document.status = DocumentStatus.SPLITTNG
            document.parsing_completed_at = datetime.now()
            document.character_count = character_count

        logging.info(
            f"Document {document.id} parsing completed, character count: {character_count}"
        )
        return langchain_docs

    def _splitting(self, document: Document, langchain_docs: list[LangchainDocument]):
        logging.info(f"Start splitting document {document.id}")

        process_rule = self.db.session.query(ProcessRule).get(document.process_rule_id)

        text_splitter = self.process_rule_service.get_text_splitter_by_process_rule(
            process_rule=process_rule,
            length_function=self.embedding_service.calculate_token_count,
        )

        # 清除多余字符
        for langchain_doc in langchain_docs:
            langchain_doc.page_content = (
                self.process_rule_service.clean_text_by_process_rule(
                    process_rule=process_rule, text=langchain_doc.page_content
                )
            )

        # 分割文档
        langchain_segments = text_splitter.split_documents(langchain_docs)

        # 存储 segment，更新 document 状态为分割完成
        position = (
            self.db.session.query(func.coalesce(func.max(Segment.position), 0))
            .filter(
                Segment.document_id == document.id,
            )
            .scalar()
        )
        segments = []
        doc_token_count = 0
        for langchain_segment in langchain_segments:
            position += 1
            content = langchain_segment.page_content
            token_count = self.embedding_service.calculate_token_count(content)
            doc_token_count += token_count
            segment = Segment(
                account_id=document.account_id,
                dataset_id=document.dataset_id,
                document_id=document.id,
                node_id=uuid4(),
                position=position,
                content=content,
                character_count=len(content),
                token_count=token_count,
                hash=generate_text_hash(content),
                status=SegmentStatus.WAITING,
            )
            segments.append(segment)

        with self.db.auto_commit():
            self.db.session.add_all(segments)
            document.token_count = doc_token_count
            document.status = DocumentStatus.INDEXING
            document.splitting_completed_at = datetime.now()

        for index, langchain_segment in enumerate(langchain_segments):
            segment = segments[index]
            langchain_segment.metadata = {
                "account_id": str(segment.account_id),
                "dataset_id": str(segment.dataset_id),
                "document_id": str(segment.document_id),
                "segment_id": str(segment.id),
                "node_id": str(segment.node_id),
                "document_enabled": False,
                "segment_enabled": False,
            }

        logging.info(
            f"Document {document.id} splitting completed, segment count: {len(segments)}"
        )
        return langchain_segments

    def _indexing(
        self,
        document: Document,
        langchain_segments: list[LangchainDocument],
        keyword_table_record: KeywordTable,
    ):
        logging.info(f"Start indexing document {document.id}")
        keyword_table = {
            keyword: set(value)
            for keyword, value in keyword_table_record.keyword_table.items()
        }
        with self.db.auto_commit():
            count = 0
            for langchain_segment in langchain_segments:
                count += 1
                keywords = self.jieba_service.extract_keywords(
                    langchain_segment.page_content, 10
                )

                self.db.session.query(Segment).filter(
                    Segment.id == langchain_segment.metadata["segment_id"]
                ).update(
                    {
                        "keywords": keywords,
                        "status": SegmentStatus.INDEXING,
                        "indexing_completed_at": datetime.now(),
                    }
                )
                if count % 200 == 0:
                    self.db.session.flush()

                for keyword in keywords:
                    if keyword not in keyword_table:
                        keyword_table[keyword] = set()
                    keyword_table[keyword].add(langchain_segment.metadata["segment_id"])

        logging.info(f"Document {document.id} all segments indexed")

        with self.db.auto_commit():
            keyword_table_record.keyword_table = {
                keyword: list(value) for keyword, value in keyword_table.items()
            }

            document.indexing_completed_at = datetime.now()

        logging.info(
            f"Document {document.id} indexing completed, keyword table updated"
        )

    def _completed(
        self, document: Document, langchain_segments: list[LangchainDocument]
    ):
        logging.info(f"Start completing document {document.id}")

        for langchain_segment in langchain_segments:
            langchain_segment.metadata["document_enabled"] = True
            langchain_segment.metadata["segment_enabled"] = True

        def thread_func(
            flask_app: Flask, chunks: list[LangchainDocument], ids: list[UUID]
        ) -> None:
            with flask_app.app_context():
                self.vector_store_service.vector_store.add_documents(
                    documents=chunks,
                    ids=ids,
                )

                with self.db.auto_commit():
                    self.db.session.query(Segment).filter(
                        Segment.node_id.in_(ids)
                    ).update(
                        {
                            "status": SegmentStatus.COMPLETED,
                            "completed_at": datetime.now(),
                            "enabled": True,
                        }
                    )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(0, len(langchain_segments), 10):
                chunks = langchain_segments[i : i + 10]
                ids = [str(chunk.metadata["node_id"]) for chunk in chunks]

                futures.append(
                    executor.submit(
                        thread_func, current_app._get_current_object(), chunks, ids
                    )
                )

        # 等待所有线程完成
        for future in futures:
            future.result()

        logging.info(f"Document {document.id} all segments completed")

        with self.db.auto_commit():
            document.status = DocumentStatus.COMPLETED
            document.completed_at = datetime.now()
            document.enabled = True

        logging.info(f"Document {document.id} completed")

    @classmethod
    def _clean_extra_text(cls, text: str) -> str:
        """清除过滤传递的多余空白字符串"""
        text = re.sub(r"<\|", "<", text)
        text = re.sub(r"\|>", ">", text)
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\xEF\xBF\xBE]", "", text)
        text = re.sub("\uFFFE", "", text)  # 删除零宽非标记字符
        return text

    def update_document_enabled(
        self, document_id: UUID, lock_key: str, lock_value: str, enabled: bool
    ):
        try:
            document = (
                self.db.session.query(Document)
                .filter(Document.id == document_id)
                .one_or_none()
            )
            if not document:
                logging.error(f"Document {document_id} not found")
                return
            if document.enabled != enabled:
                logging.error(
                    f"Document {document_id} enabled status is not equal to {enabled}"
                )
                return

            segments = (
                self.db.session.query(Segment)
                .with_entities(Segment.id, Segment.node_id, Segment.enabled)
                .filter(
                    Segment.document_id == document_id,
                    Segment.status == SegmentStatus.COMPLETED,
                )
                .all()
            )

            node_ids = [node_id for _, node_id, _ in segments]
            segment_ids = [segment_id for segment_id, _, _ in segments]

            collection = self.vector_store_service.collection
            for node_id in node_ids:
                try:
                    collection.data.update(
                        uuid=node_id,
                        properties={"document_enabled": enabled},
                    )
                except Exception as e:
                    with self.db.auto_commit():
                        self.db.session.query(Segment).filter(
                            Segment.node_id == node_id
                        ).update(
                            {
                                "error": str(e),
                                "status": SegmentStatus.ERROR,
                                "enabled": False,
                                "disabled_at": datetime.now(),
                                "stopped_at": datetime.now(),
                            }
                        )
                    logging.error(f"Update segment {node_id} enabled failed, {e}")

            if enabled is True:
                enabled_segment_ids = [
                    id for id, _, enabled in segments if enabled is True
                ]
                self.keyword_table_service.add_keyword_table_from_ids(
                    document.dataset_id, enabled_segment_ids
                )
            else:
                self.keyword_table_service.delete_keyword_table_from_ids(
                    document.dataset_id, segment_ids
                )

        except Exception as e:
            logging.error(f"Update document enabled failed, {e}")
            origin_enabled = not enabled
            with self.db.auto_commit():
                self.db.session.query(Document).filter(
                    Document.id == document_id
                ).update(
                    {
                        "enabled": origin_enabled,
                        "disabled_at": None if origin_enabled else datetime.now(),
                    }
                )
        finally:
            release_lock(self.redis_client, lock_key, lock_value)
            logging.info(f"释放锁 {lock_key} {lock_value}")

    def delete_document(self, dataset_id: UUID, document_id: UUID):
        segment_ids = [
            str(id)
            for id, in self.db.session.query(Segment)
            .with_entities(Segment.id)
            .filter(
                Segment.document_id == document_id,
            )
            .all()
        ]

        collection = self.vector_store_service.collection
        collection.data.delete_many(
            where=Filter.by_property("document_id").equal(document_id)
        )

        with self.db.auto_commit():
            self.db.session.query(Segment).filter(
                Segment.document_id == document_id
            ).delete()

        self.keyword_table_service.delete_keyword_table_from_ids(
            dataset_id=dataset_id, segment_ids=segment_ids
        )

"""
@Time   : 2024/12/21 22:05
@Author : Leslie
@File   : full_text_retriever.py
"""

from uuid import UUID
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from pkg.sqlalchemy import SQLAlchemy
from internal.service import JiebaService
from internal.model import KeywordTable, Segment
from collections import Counter
from langchain_core.documents import Document as LCDocument


class FullTextRetriever(BaseRetriever):
    dataset_ids: list[UUID]
    db: SQLAlchemy
    jieba_service: JiebaService
    search_kwargs: dict = Field(default_factory=dict)

    def _get_relevant_documents(self, query, *, run_manager):
        query_key_words = self.jieba_service.extract_keywords(query, 10)

        all_keyword_tables = [
            keyword_table
            for keyword_table, in self.db.session.query(KeywordTable)
            .with_entities(KeywordTable.keyword_table)
            .filter(KeywordTable.dataset_id.in_(self.dataset_ids))
            .all()
        ]

        all_segment_ids = []
        for keyword_table in all_keyword_tables:
            for keyword, ids in keyword_table.items():
                if keyword in query_key_words:
                    all_segment_ids.extend(ids)

        id_counter = Counter(all_segment_ids)
        k = self.search_kwargs.get("k", 4)
        top_k = id_counter.most_common(k)

        top_k_ids = [id for id, _ in top_k]

        segments = (
            self.db.session.query(Segment).filter(Segment.id.in_(top_k_ids)).all()
        )
        segment_dict = {str(segment.id): segment for segment in segments}

        sorted_segments = [
            segment_dict[str(id)] for id in top_k_ids if id in segment_dict
        ]

        lc_documents = [
            LCDocument(
                page_content=segment.content,
                metadata={
                    "account_id": str(segment.account_id),
                    "dataset_id": str(segment.dataset_id),
                    "document_id": str(segment.document_id),
                    "segment_id": str(segment.id),
                    "node_id": str(segment.node_id),
                    "document_enabled": True,
                    "segment_enabled": True,
                    "score": 0,
                },
            )
            for segment in sorted_segments
        ]

        return lc_documents

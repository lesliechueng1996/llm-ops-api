"""
@Time   : 2024/12/22 00:07
@Author : Leslie
@File   : retrieval_service.py
"""

from uuid import UUID
from flask import Flask
from injector import inject
from dataclasses import dataclass

from pydantic import BaseModel, Field
from sqlalchemy import update
from internal.entity import RetrievalStrategy, RetrievalSource
from internal.lib.helper import combine_documents
from internal.model import Dataset, DatasetQuery, Segment
from internal.service.jieba_service import JiebaService
from pkg.sqlalchemy import SQLAlchemy
from .vector_store_service import VectorStoreService
from langchain.retrievers import EnsembleRetriever
from langchain_core.tools import BaseTool, tool
from internal.core.agent.entities.agent_entity import DATASET_RETRIEVAL_TOOL_NAME


@inject
@dataclass
class RetrievalService:
    db: SQLAlchemy
    vector_store_service: VectorStoreService
    jieba_service: JiebaService

    def search_in_databases(
        self,
        account_id: UUID,
        dataset_ids: list[UUID],
        query: str,
        retrieval_strategy: str = RetrievalStrategy.SEMANTIC,
        k: int = 4,
        score: float = 0,
        retrival_source: str = RetrievalSource.HIT_TESTING,
    ):
        avaliable_dataset_ids = [
            id
            for id, in self.db.session.query(Dataset)
            .with_entities(Dataset.id)
            .filter(Dataset.account_id == account_id, Dataset.id.in_(dataset_ids))
            .all()
        ]

        from internal.core.retrievers import SemanticRetriever, FullTextRetriever

        semantic_retriever = SemanticRetriever(
            dataset_ids=avaliable_dataset_ids,
            vector_store=self.vector_store_service.vector_store,
            search_kwargs={
                "k": k,
                "score_threshold": score,
            },
        )

        full_text_retriever = FullTextRetriever(
            dataset_ids=avaliable_dataset_ids,
            db=self.db,
            jieba_service=self.jieba_service,
            search_kwargs={
                "k": k,
                "score_threshold": score,
            },
        )

        hybrid_retriever = EnsembleRetriever(
            retrievers=[semantic_retriever, full_text_retriever],
            weights=[0.5, 0.5],
        )

        if retrieval_strategy == RetrievalStrategy.SEMANTIC:
            lc_documents = semantic_retriever.invoke(query)[:k]
        elif retrieval_strategy == RetrievalStrategy.FULL_TEXT:
            lc_documents = full_text_retriever.invoke(query)[:k]
        else:
            lc_documents = hybrid_retriever.invoke(query)[:k]

        with self.db.auto_commit():
            dataset_queries = []
            segment_ids = []
            unique_dataset_ids = list(
                set([lc_doc.metadata["dataset_id"] for lc_doc in lc_documents])
            )
            for dataset_id in unique_dataset_ids:
                dataset_query = DatasetQuery(
                    dataset_id=dataset_id,
                    query=query,
                    source=retrival_source,
                    source_app_id=None,
                    created_by=account_id,
                )
                dataset_queries.append(dataset_query)
            self.db.session.add_all(dataset_queries)

            for lc_doc in lc_documents:
                segment_ids.append(lc_doc.metadata["segment_id"])

            self.db.session.execute(
                update(Segment)
                .where(Segment.id.in_(segment_ids))
                .values(hit_count=Segment.hit_count + 1)
            )

        return lc_documents

    def create_langchain_tool_from_search(
        self,
        flask_app: Flask,
        account_id: UUID,
        dataset_ids: list[UUID],
        retrieval_strategy: str = RetrievalStrategy.SEMANTIC,
        k: int = 4,
        score: float = 0,
        retrival_source: str = RetrievalSource.HIT_TESTING,
    ) -> BaseTool:
        class DatasetRetrievalInput(BaseModel):
            query: str = Field(description="知识库搜索query语句，类型为字符串")

        @tool(DATASET_RETRIEVAL_TOOL_NAME, args_schema=DatasetRetrievalInput)
        def dataset_retrieval(query: str) -> str:
            """如果需要搜索扩展的知识库内容，当你觉得用户的提问超过你的知识范围时，可以尝试调用该工具，输入为搜索query语句，返回数据为检索内容字符串"""
            with flask_app.app_context():
                documents = self.search_in_databases(
                    account_id=account_id,
                    dataset_ids=dataset_ids,
                    query=query,
                    retrieval_strategy=retrieval_strategy,
                    k=k,
                    score=score,
                    retrival_source=retrival_source,
                )

            if len(documents) == 0:
                return "知识库内没有检索到对应内容"

            return combine_documents(documents)

        return dataset_retrieval

"""
@Time   : 2024/12/21 21:47
@Author : Leslie
@File   : semantic_retriever.py
"""

from uuid import UUID
from langchain_core.retrievers import BaseRetriever
from langchain_weaviate import WeaviateVectorStore
from pydantic import Field
from weaviate.classes.query import Filter


class SemanticRetriever(BaseRetriever):
    dataset_ids: list[UUID]
    vector_store: WeaviateVectorStore
    search_kwargs: dict = Field(default_factory=dict)

    def _get_relevant_documents(self, query, *, run_manager):
        k = self.search_kwargs.pop("k", 4)

        search_result = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k,
            **{
                "filters": Filter.all_of(
                    [
                        Filter.by_property("dataset_id").contains_any(
                            [str(id) for id in self.dataset_ids]
                        ),
                        Filter.by_property("document_enabled").equal(True),
                        Filter.by_property("segment_enabled").equal(True),
                    ]
                ),
                **self.search_kwargs,
            }
        )
        if search_result is None or len(search_result) == 0:
            return []

        docs = []
        for doc, score in search_result:
            doc.metadata["score"] = score
            docs.append(doc)

        return docs

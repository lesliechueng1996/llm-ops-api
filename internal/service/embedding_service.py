"""
@Time   : 2024/12/18 03:12
@Author : Leslie
@File   : embedding_service.py
"""

from injector import inject
from dataclasses import dataclass
from langchain_community.storage import RedisStore
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from redis import Redis
import os
import tiktoken


@inject
@dataclass
class EmbeddingService:
    _store: RedisStore
    _embeddings: HuggingFaceEmbeddings
    _cache_backed_embeddings: CacheBackedEmbeddings

    def __init__(self, redis: Redis):
        self._store = RedisStore(client=redis)
        self._embeddings = HuggingFaceEmbeddings(
            model_name="Alibaba-NLP/gte-multilingual-base",
            cache_folder=os.path.join(os.getcwd(), "internal", "core", "embeddings"),
            model_kwargs={"trust_remote_code": True},
        )
        self._cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
            self._embeddings,
            self._store,
            namespace="embeddings",
        )

    def calculate_token_count(self, text: str) -> int:
        encoding = tiktoken.encoding_for_model("gpt-3.5")
        return len(encoding.encode(text))

    @property
    def embeddings(self) -> CacheBackedEmbeddings:
        return self._cache_backed_embeddings

    @property
    def store(self) -> RedisStore:
        return self._store

    @property
    def cache_backed_embeddings(self) -> CacheBackedEmbeddings:
        return self._cache_backed_embeddings

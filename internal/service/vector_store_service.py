from os import getenv
from weaviate import WeaviateClient, connect_to_local
from langchain_weaviate import WeaviateVectorStore
from injector import inject
from langchain_core.documents import Document
from internal.service.embedding_service import EmbeddingService

COLLECTION_NAME = "Dataset"


@inject
class VectorStoreService:
    client: WeaviateClient
    vector_store: WeaviateVectorStore

    def __init__(self, embedding_service: EmbeddingService):
        self.client = connect_to_local(
            host=getenv("WEAVIATE_HOST"), port=int(getenv("WEAVIATE_PORT"))
        )
        self.vector_store = WeaviateVectorStore(
            client=self.client,
            index_name=COLLECTION_NAME,
            text_key="text",
            embedding=embedding_service.embeddings,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever()

    @property
    def collection(self):
        return self.client.collections.get(COLLECTION_NAME)

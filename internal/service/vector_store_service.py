from os import getenv
from weaviate import WeaviateClient, connect_to_local
from langchain_weaviate import WeaviateVectorStore
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from injector import inject
from langchain_core.documents import Document


@inject
class VectorStoreService:
    client: WeaviateClient
    vector_store: WeaviateVectorStore

    def __init__(self):
        self.client = connect_to_local(
            host=getenv("WEAVIATE_HOST"), port=int(getenv("WEAVIATE_PORT"))
        )
        self.vector_store = WeaviateVectorStore(
            client=self.client,
            index_name="DatasetDemo",
            text_key="text",
            embedding=QianfanEmbeddingsEndpoint(),
        )

    def get_retriever(self):
        return self.vector_store.as_retriever()

    @classmethod
    def combine_documents(cls, documents: list[Document]):
        return "\n\n".join([doc.page_content for doc in documents])

from langchain_cohere import CohereRerank
from langchain_weaviate import WeaviateVectorStore
import weaviate
from weaviate.classes.init import Auth
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from os import getenv
from dotenv import load_dotenv
from langchain.retrievers import ContextualCompressionRetriever

load_dotenv()


rerank = CohereRerank(model="rerank-multilingual-v3.0")

db_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=getenv("WEAVIATE_CLOUD_HOST"),
    auth_credentials=Auth.api_key(getenv("WEAVIATE_CLOUD_API_KEY")),
    skip_init_checks=True,
)

vector_store = vector_store = WeaviateVectorStore(
    client=db_client,
    text_key="text",
    embedding=QianfanEmbeddingsEndpoint(),
    index_name="ParentDocument",
)

retriever = ContextualCompressionRetriever(
    base_compressor=rerank,
    base_retriever=vector_store.as_retriever(search_type="mmr"),
)

search_docs = retriever.invoke("分享关于LLMOps的一些应用配置")
print(search_docs)
print(len(search_docs))

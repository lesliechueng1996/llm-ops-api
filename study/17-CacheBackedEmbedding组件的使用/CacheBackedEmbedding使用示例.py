from dotenv import load_dotenv
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain.storage import LocalFileStore

load_dotenv()

embedding = QianfanEmbeddingsEndpoint(model="Embedding-V1")
cache_backed_embeddings = CacheBackedEmbeddings.from_bytes_store(
    embedding,
    LocalFileStore("./study/17-CacheBackedEmbedding组件的使用/.cache/"),
    namespace=embedding.model,
    query_embedding_cache=True,
)

query_vector = cache_backed_embeddings.embed_query("我是Leslie，我喜欢打篮球")
document_vector = cache_backed_embeddings.embed_documents(
    ["我叫Leslie，我喜欢打篮球", "这个喜欢打篮球的人，叫Leslie", "求知若渴，虚心若愚"]
)
print(len(query_vector))
print(len(document_vector))

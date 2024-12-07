from langchain_weaviate.vectorstores import WeaviateVectorStore
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
from os import getenv
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_core.runnables import ConfigurableField

load_dotenv()


client = weaviate.connect_to_weaviate_cloud(
    cluster_url=getenv("WEAVIATE_CLOUD_HOST"),
    auth_credentials=Auth.api_key(getenv("WEAVIATE_CLOUD_API_KEY")),
    skip_init_checks=True,
)
vector_store = WeaviateVectorStore(
    client=client,
    text_key="text",
    embedding=QianfanEmbeddingsEndpoint(),
    index_name="DatasetDemo",
)

retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.5},
).configurable_fields(
    search_type=ConfigurableField(id="retriever_search_type"),
    search_kwargs=ConfigurableField(id="retriever_search_kwargs"),
)

results = retriever.with_config(
    config={
        "configurable": {
            "retriever_search_type": "mmr",
            "retriever_search_kwargs": {"k": 5},
        }
    }
).invoke("关于配置接口的信息有哪些")

for result in results:
    print(result.page_content[:100])
    print("===================")
client.close()

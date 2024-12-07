import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
from os import getenv
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_weaviate import WeaviateVectorStore
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.chat_models import MoonshotChat
from langchain_core.prompts import ChatPromptTemplate

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

retriever = vector_store.as_retriever(search_type="mmr")

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), temperature=0),
    prompt=ChatPromptTemplate.from_template(
        "您是一款AI语言模型助手。您的任务是生成3个不同版本的用户问题，以便从向量数据库中检索相关文档。"
        "通过从多个角度改写用户问题，您的目标是帮助用户克服基于距离的相似性搜索的一些局限性。"
        "请将这些改写后的问题用换行符分隔开。"
        "原始问题：{question}"
    ),
    include_original=True,
)

docs = multi_query_retriever.invoke("关于LLMOps应用配置的文档有哪些")
for doc in docs:
    print(doc.page_content[:100])
    print("===================")

client.close()

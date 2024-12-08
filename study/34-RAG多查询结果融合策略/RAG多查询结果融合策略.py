from os import getenv
from typing import List
from dotenv import load_dotenv
from langchain_core.load import dumps, loads
from langchain.retrievers import MultiQueryRetriever
from langchain_core.documents import Document
from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_weaviate import WeaviateVectorStore
import weaviate
from weaviate.classes.init import Auth
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.chat_models import MoonshotChat
from langchain_core.prompts import ChatPromptTemplate


class RAGFusionRetriever(MultiQueryRetriever):
    k: int = 4

    def retrieve_documents(
        self, queries: List[str], run_manager: CallbackManagerForRetrieverRun
    ) -> List[List]:
        documents = []
        for query in queries:
            docs = self.retriever.invoke(
                query, config={"callbacks": run_manager.get_child()}
            )
            documents.append(docs)
        return documents

    def unique_union(self, documents: List[List]) -> List[Document]:
        fused_result = {}
        for result in documents:
            for index, doc in enumerate(result):
                doc_str = dumps(doc)
                if doc_str not in fused_result:
                    fused_result[doc_str] = 0
                fused_result[doc_str] += 1 / (index + 60)
        sorted_docs = [
            (loads(doc_str), score)
            for doc_str, score in sorted(
                fused_result.items(), key=lambda x: x[1], reverse=True
            )
        ]
        return [doc[0] for doc in sorted_docs[: self.k]]


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

multi_query_retriever = RAGFusionRetriever.from_llm(
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

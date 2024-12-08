from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.language_models import BaseChatModel
from langchain_weaviate import WeaviateVectorStore
import weaviate
from weaviate.classes.init import Auth
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from os import getenv
from dotenv import load_dotenv
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import StrOutputParser


load_dotenv()


class HyDERetriever(BaseRetriever):
    retriever: BaseRetriever
    llm: BaseChatModel

    def _get_relevant_documents(self, query: str, *, run_manager):
        prompt = ChatPromptTemplate.from_template(
            "请写一篇500字以内的科学论文来回答这个问题。\n问题：{question}\n文章："
        )

        chain = (
            {
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
            | StrOutputParser()
            | self.retriever
        )

        return chain.invoke(query)


db_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=getenv("WEAVIATE_CLOUD_HOST"),
    auth_credentials=Auth.api_key(getenv("WEAVIATE_CLOUD_API_KEY")),
    skip_init_checks=True,
)

vector_store = WeaviateVectorStore(
    client=db_client,
    text_key="text",
    embedding=QianfanEmbeddingsEndpoint(),
    index_name="DatasetDemo",
)
retriever = vector_store.as_retriever(search_type="mmr")

hy_de_retriever = HyDERetriever(
    retriever=retriever,
    llm=MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), temperature=0),
)

docs = hy_de_retriever.invoke("关于LLMOps应用配置的文档有哪些？")
for doc in docs:
    print(doc)

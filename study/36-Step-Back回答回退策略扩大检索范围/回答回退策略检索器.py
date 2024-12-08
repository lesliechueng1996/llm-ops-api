from os import getenv
from dotenv import load_dotenv
from langchain_core.retrievers import BaseRetriever
from langchain_community.chat_models import MoonshotChat
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_weaviate import WeaviateVectorStore
import weaviate
from weaviate.classes.init import Auth
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

load_dotenv()


class StepBackRetriever(BaseRetriever):
    retriever: BaseRetriever
    llm: BaseChatModel

    def _get_relevant_documents(self, query: str, *, run_manager):
        examples = [
            {
                "input": "慕课网上有关于AI应用开发的课程么？",
                "output": "慕课网上有哪些课程？",
            },
            {
                "input": "慕小课出生在哪个国家？",
                "output": "慕小课的人生经历是什么样的？",
            },
            {
                "input": "司机可以开快车么？",
                "output": "司机可以做什么？",
            },
        ]

        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个世界知识的专家，你的任务是回退问题，将问题改述为一般或者前置问题，这样更容易回答，请参考示例来实现。",
                ),
                few_shot_prompt,
                ("human", "{query}"),
            ]
        )

        chain = (
            {"query": RunnablePassthrough()}
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

step_back_retriever = StepBackRetriever(
    retriever=retriever,
    llm=MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), temperature=0),
)

docs = step_back_retriever.invoke("人工智能会让世界发生翻天覆地的变化吗？")
for doc in docs:
    print(doc)

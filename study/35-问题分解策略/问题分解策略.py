from os import getenv
from typing import List
from dotenv import load_dotenv
import weaviate
from operator import itemgetter
from weaviate.classes.init import Auth
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_weaviate import WeaviateVectorStore
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

load_dotenv()

decomposition_prompt = ChatPromptTemplate.from_template(
    "你是一个乐于助人的AI助理，可以针对一个输入问题生成多个相关的子问题。\n"
    "目标是将输入问题分解成一组可以独立回答的子问题或者子任务。\n"
    "生成与以下问题相关的多个搜索查询：{question}\n"
    "并使用换行符进行分割，输出（3个子问题/子查询）"
)

decomposition_chain: RunnableSerializable[str, List[str]] = (
    {"question": RunnablePassthrough()}
    | decomposition_prompt
    | MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), temperature=0)
    | StrOutputParser()
    | (lambda x: x.strip().split("\n"))
)

question = "关于LLMOps应用配置的文档有哪些"
sub_questions = decomposition_chain.invoke(question)

prompt = ChatPromptTemplate.from_template(
    """这是你需要回答的问题：
---
{question}
---

这是所有可用的背景问题和答案对：
---
{qa_pairs}
---

这是与问题相关的额外背景信息：
---
{context}
---
"""
)

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

chain = (
    RunnablePassthrough.assign(context=itemgetter("question") | retriever)
    | prompt
    | MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), temperature=0)
    | StrOutputParser()
)

qa_pairs = ""
for sub_question in sub_questions:
    answer = chain.invoke({"question": sub_question, "qa_pairs": qa_pairs})
    qa_pair = f"Question: {sub_question}\nAnswer: {answer}".strip()
    qa_pairs += "\n---\n" + qa_pair
    print(f"问题: {sub_question}")
    print(f"回答: {answer}")

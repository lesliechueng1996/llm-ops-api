from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain.utils.math import cosine_similarity
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.chat_models import MoonshotChat
from os import getenv
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

physics_template = """你是一位非常聪明的物理教授。
你擅长以简洁易懂的方式回答物理问题。
当你不知道问题的答案时，你会坦率承认自己不知道。

这是一个问题：
{query}
"""

math_templage = """你是一位非常优秀的数学家。你擅长回答数学问题。
你之所以如此优秀，是因为你能将复杂的问题分解成多个小步骤。
并且回答这些小步骤，然后将它们整合在一起来回答更广泛的问题。

这是一个问题：
{query}
"""

embedding = QianfanEmbeddingsEndpoint()
prompt_templates = [physics_template, math_templage]
prompt_embeddings = embedding.embed_documents(prompt_templates)


def prompt_router(input) -> ChatPromptTemplate:
    query_embedding = embedding.embed_query(input["query"])
    similarity = cosine_similarity([query_embedding], prompt_embeddings)[0]
    most_similar = prompt_templates[similarity.argmax()]
    print("使用数学模版" if most_similar == math_templage else "使用物理模版")
    return ChatPromptTemplate.from_template(most_similar)


chain = (
    {"query": RunnablePassthrough()}
    | RunnableLambda(prompt_router)
    | MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"))
    | StrOutputParser()
)

print(chain.invoke("黑洞是什么？"))
print("====================================")
print(chain.invoke("能介绍下勾股定理计算公式么？"))

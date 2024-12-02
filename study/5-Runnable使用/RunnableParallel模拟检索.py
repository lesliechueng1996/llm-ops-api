from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables import RunnableParallel
from dotenv import load_dotenv
import os

load_dotenv()


def retrieval(query: str):
    print(f"Retrieval: {query}")
    return "我是小明"


prompt = ChatPromptTemplate.from_template(
    """请根据上下文回答用户的问题

<context>
{context}
</context>

用户的问题是: {query}
"""
)
chat = MoonshotChat(moonshot_api_key=os.getenv("OPENAI_API_KEY"))
parser = StrOutputParser()

# chain = (
#     RunnableParallel(
#         {
#             "context": lambda x: retrieval(x["query"]),
#             "query": itemgetter("query"),
#         }
#     )
#     | prompt
#     | chat
#     | parser
# )

chain = (
    {
        "context": lambda x: retrieval(x["query"]),
        "query": itemgetter("query"),
    }
    | prompt
    | chat
    | parser
)

content = chain.invoke({"query": "你好，我是谁?"})
print(content)

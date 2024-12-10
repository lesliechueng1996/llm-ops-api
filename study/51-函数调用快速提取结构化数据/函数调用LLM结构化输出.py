from os import getenv
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()


class QAExtra(BaseModel):
    """这是一个问答键值对工具，传递对应的假设性问题和答案"""

    question: str = Field(description="假设性问题")
    answer: str = Field(description="假设性问题对应的答案")


llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
    temperature=0,
)

structured_llm = llm.with_structured_output(QAExtra)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "请从用户传递的问题中提取出假设性问题和答案"),
        ("human", "{query}"),
    ]
)
chain = {"query": RunnablePassthrough()} | prompt | structured_llm

print(chain.invoke("我喜欢游泳，打篮球"))

from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()


class RouteQuery(BaseModel):
    datasource: Literal["python_docs", "js_docs", "golang_docs"] = Field(
        description="根据给定用户问题，选择哪个数据源最相关以回答他们的问题"
    )


def choose_route(result: RouteQuery) -> str:
    if "python_docs" in result.datasource:
        return "chain in python_docs"
    elif "js_docs" in result.datasource:
        return "chain in js_docs"
    return "chain in golang_docs"


chat = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
    temperature=0,
)
chat_with_struct = chat.with_structured_output(RouteQuery)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个擅长将用户问题路由到适当的数据源的专家。\n请根据问题涉及的编程语言，将其路由到相关数据源。",
        ),
        ("human", "{question}"),
    ]
)

router = {"question": RunnablePassthrough()} | prompt | chat_with_struct | choose_route

question = """为什么下面的代码不工作了，请帮我检查下：
var a = 1;
console.log(a);
"""

print(router.invoke(question))

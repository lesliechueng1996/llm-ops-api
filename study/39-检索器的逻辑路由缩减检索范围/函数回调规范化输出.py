from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv()


class RouteQuery(BaseModel):
    datasource: Literal["python_docs", "js_docs", "golang_docs"] = Field(
        description="根据给定用户问题，选择哪个数据源最相关以回答他们的问题"
    )


print(getenv("OPENAI_KEY"))
print(getenv("OPENAI_API_URL"))
chat = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
    temperature=0,
)
chat_with_struct = chat.with_structured_output(RouteQuery)
question = """为什么下面的代码不工作了，请帮我检查下：
var a = 1;
console.log(a);
"""

print(chat_with_struct.invoke(question))

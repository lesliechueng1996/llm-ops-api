from dotenv import load_dotenv
from os import getenv
from pydantic import BaseModel, Field
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具传递的参数是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)
tools = [google_serper]

llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
    temperature=0,
)

agent = create_react_agent(
    model=llm,
    tools=tools,
)
state = agent.invoke(
    {"messages": [("human", "2024年北京半程马拉松的前三名成绩是多少？")]}
)
for msg in state["messages"]:
    print("消息类型: ", msg.type)
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        print("工具调用参数: ", msg.tool_calls)
    print("消息内容: ", msg.content)
    print("===========================================")

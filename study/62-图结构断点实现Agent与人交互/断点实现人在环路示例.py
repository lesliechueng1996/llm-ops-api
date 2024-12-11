from dotenv import load_dotenv
from os import getenv
from pydantic import BaseModel, Field
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState

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

llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
)

tools = [google_serper]

agent = create_react_agent(
    model=llm,
    tools=tools,
    checkpointer=MemorySaver(),
    interrupt_before=["tools"],
)

config = {"configurable": {"thread_id": 1}}
agent.invoke({"messages": [("human", "马拉松的世界纪录是多少？")]}, config=config)

state = agent.get_state(config)[0]
print("current state: ", state)
last_message = state["messages"][-1]
if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
    print("工具调用: ", last_message.tool_calls)
    answer = input("同意调用工具输入yes: ")
    if answer.lower() == "yes":
        print("结果: ", agent.invoke(None, config=config))

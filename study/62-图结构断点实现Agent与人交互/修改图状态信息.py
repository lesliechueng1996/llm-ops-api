from dotenv import load_dotenv
from os import getenv
from pydantic import BaseModel, Field
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import ToolMessage

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
    interrupt_after=["tools"],
)

config = {"configurable": {"thread_id": 1}}
agent.invoke({"messages": [("human", "马拉松的世界纪录是多少？")]}, config=config)

state = agent.get_state(config)[0]
last_message = state["messages"][-1]
print("last_message: ", last_message)
print("======================================")

tool_message = ToolMessage(
    id=last_message.id,
    name=last_message.name,
    tool_call_id=last_message.tool_call_id,
    content="新华社美国芝加哥10月8日电当地时间8日鸣枪的2023年芝加哥马拉松赛中，来自中国的张三以2小时0分35秒的成绩完赛，创造新的男子马拉松世界纪录。",
)

agent.update_state(config=config, values={"messages": [tool_message]})

print("结果: ", agent.invoke(None, config=config))

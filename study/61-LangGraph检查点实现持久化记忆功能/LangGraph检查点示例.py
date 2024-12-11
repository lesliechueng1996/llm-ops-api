from os import getenv
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
)

checkpointer = MemorySaver()
agent = create_react_agent(
    model=llm,
    tools=[],
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": 1}}

print(agent.invoke({"messages": [("human", "你好，我是慕小克，你是？")]}, config))

print(agent.invoke({"messages": [("human", "你记得我叫什么名字么")]}, config))

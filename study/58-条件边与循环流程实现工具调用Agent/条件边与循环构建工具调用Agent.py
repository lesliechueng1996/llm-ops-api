from dotenv import load_dotenv
from os import getenv
from pydantic import BaseModel, Field
from typing import TypedDict, List, Annotated, Literal
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.graph import add_messages, StateGraph, START, END
from langchain_core.messages import ToolMessage, AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

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
llm_with_tools = llm.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


def chatbot(state: State, config: dict):
    ai_message = llm_with_tools.invoke(state["messages"])
    return {"messages": [ai_message]}


# def tool_executor(state: State, config: dict):
#     tool_map = {tool.name: tool for tool in tools}
#     ai_message = state["messages"][-1]
#     tool_calls = ai_message.tool_calls
#     tool_messages = []
#     for tool_call in tool_calls:
#         tool = tool_map[tool_call["name"]]
#         tool_message = ToolMessage(
#             tool_call_id=tool_call["id"],
#             content=tool.invoke(tool_call["args"]),
#             name=tool_call["name"],
#         )
#         tool_messages.append(tool_message)
#     return {"messages": tool_messages}


def chatbot_router(state: State, config: dict) -> Literal["tool_executor", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tool_executor"
    return END


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
# graph_builder.add_node("tool_executor", tool_executor)
graph_builder.add_node("tool_executor", ToolNode(tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", chatbot_router)
graph_builder.add_edge("tool_executor", "chatbot")

graph = graph_builder.compile()

state = graph.invoke(
    {"messages": [("human", "2024年北京半程马拉松的前三名成绩是多少？")]}
)

for msg in state["messages"]:
    print("消息类型: ", msg.type)
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        print("工具调用参数: ", msg.tool_calls)
    print("消息内容: ", msg.content)
    print("===========================================")

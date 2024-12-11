from os import getenv
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.output_parsers import StrOutputParser


load_dotenv()


# 工具
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


# 归纳函数
def reduce_str(left: str | None, right: str | None) -> str:
    if right is not None and right != "":
        return right
    return left


# 父图状态
class AgentState(TypedDict):
    query: Annotated[str, reduce_str]
    live_content: Annotated[str, reduce_str]
    xhs_content: Annotated[str, reduce_str]


# 直播文案子图状态
class LiveAgentState(AgentState, MessagesState):
    pass


# 小红书文案子图状态
class XhsAgentState(AgentState):
    pass


# 直播文案子图
live_graph = StateGraph(LiveAgentState)


def live_chatbot(state: LiveAgentState, config: dict):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个拥有10年经验的直播文案专家，请根据用户提供的产品整理一篇直播带货脚本文案，如果在你的知识库内找不到关于该产品的信息，可以使用搜索工具。",
            ),
            ("human", "{query}"),
            MessagesPlaceholder("history"),
        ]
    )
    chain = prompt | llm_with_tools
    ai_message = chain.invoke(
        {
            "query": state["query"],
            "history": state["messages"],
        }
    )
    return {"messages": [ai_message], "live_content": ai_message.content}


live_graph.add_node("live_chatbot", live_chatbot)
live_graph.add_node("tools", ToolNode(tools))

live_graph.add_edge(START, "live_chatbot")
live_graph.add_conditional_edges("live_chatbot", tools_condition)
live_graph.add_edge("tools", "live_chatbot")


# 小红书文案子图
xhs_graph = StateGraph(XhsAgentState)


def xhs_chatbot(state: XhsAgentState, config: dict):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个小红书文案大师，请根据用户传递的商品名，生成一篇关于该商品的小红书笔记文案，注意风格活泼，多使用 emoji 表情。",
            ),
            ("human", "{query}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"query": state["query"]})
    return {"xhs_content": result}


xhs_graph.add_node("xhs_chatbot", xhs_chatbot)

xhs_graph.add_edge(START, "xhs_chatbot")
xhs_graph.add_edge("xhs_chatbot", END)


# 父图
graph_builder = StateGraph(AgentState)


def parallel_node(state: AgentState, config: dict):
    return state


graph_builder.add_node("parallel_node", parallel_node)
graph_builder.add_node("live_agent", live_graph.compile())
graph_builder.add_node("xhs_agent", xhs_graph.compile())

graph_builder.add_edge(START, "parallel_node")
graph_builder.add_edge("parallel_node", "live_agent")
graph_builder.add_edge("parallel_node", "xhs_agent")
graph_builder.add_edge("live_agent", END)
graph_builder.add_edge("xhs_agent", END)

graph = graph_builder.compile()

print(graph.invoke({"query": "潮汕牛肉丸"}))

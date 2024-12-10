from dotenv import load_dotenv
from os import getenv
from langgraph.graph import START, END, add_messages, StateGraph
from typing import TypedDict, Annotated
from langchain_community.chat_models import MoonshotChat

load_dotenv()

chat = MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"))


class State(TypedDict):
    messages: Annotated[list, add_messages]
    username: str


graph_builder = StateGraph(State)


def chatbot(state: State, config: dict):
    ai_message = chat.invoke(state["messages"])
    return {"messages": [ai_message]}


graph_builder.add_node("llm", chatbot)
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)

graph = graph_builder.compile()

print(graph.invoke({"messages": [("human", "你好，你是谁？")], "username": "test"}))

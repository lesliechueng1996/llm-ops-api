from os import getenv
from dotenv import load_dotenv
from langchain_community.chat_models import MoonshotChat
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import RemoveMessage, AIMessage

load_dotenv()

llm = MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"))


def chatbot(state: MessagesState, config: dict) -> MessagesState:
    ai_message = llm.invoke(state["messages"])
    return {"messages": [ai_message]}


def del_human_message(state: MessagesState, config: dict) -> MessagesState:
    human_message = state["messages"][0]
    return {"messages": [RemoveMessage(id=human_message.id)]}


def update_ai_message(state: MessagesState, config: dict) -> MessagesState:
    ai_message = state["messages"][-1]
    return {
        "messages": [
            AIMessage(id=ai_message.id, content=f"更改后的消息: {ai_message.content}")
        ]
    }


graph_builder = StateGraph(MessagesState)

graph_builder.add_node("llm", chatbot)
graph_builder.add_node("del_human_message", del_human_message)
graph_builder.add_node("update_ai_message", update_ai_message)

graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", "del_human_message")
graph_builder.add_edge("del_human_message", "update_ai_message")
graph_builder.add_edge("update_ai_message", END)

graph = graph_builder.compile()

state = graph.invoke({"messages": [("human", "你好")]})
print(state)

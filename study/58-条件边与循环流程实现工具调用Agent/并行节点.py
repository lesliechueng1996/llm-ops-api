from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import AIMessage, HumanMessage


def chatbot(state: MessagesState, config: dict):
    return {"messages": [AIMessage(content="你好，我是聊天机器人。")]}


def parallel1(state: MessagesState, config: dict):
    print("并行1: ", state)
    return {"messages": [HumanMessage(content="并行1")]}


def parallel2(state: MessagesState, config: dict):
    print("并行2: ", state)
    return {"messages": [HumanMessage(content="并行2")]}


def chat_end(state: MessagesState, config: dict):
    print("结束: ", state)
    return {"messages": [HumanMessage(content="对话结束。")]}


graph_builder = StateGraph(MessagesState)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("parallel1", parallel1)
graph_builder.add_node("parallel2", parallel2)
graph_builder.add_node("chat_end", chat_end)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "parallel1")
graph_builder.add_edge("chatbot", "parallel2")
graph_builder.add_edge("parallel2", "chat_end")
graph_builder.add_edge("chat_end", END)

graph = graph_builder.compile()
print(graph.invoke({"messages": [HumanMessage(content="你好。")]}))

from dotenv import load_dotenv
from os import getenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import FileChatMessageHistory

session = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session:
        session[session_id] = FileChatMessageHistory(
            f"study/10-RunnableWithMessageHistory简化/{session_id}.text"
        )
    return session[session_id]


load_dotenv()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个聊天机器人，请根据用户问题作出回答"),
        MessagesPlaceholder("history"),
        ("human", "{query}"),
    ]
)

chat = MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"))

chain = prompt | chat | StrOutputParser()

with_message_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="query",
    history_messages_key="history",
)

while True:
    query = input("Human: ")
    if query == "q":
        exit(0)
    response = with_message_chain.stream(
        {"query": query}, config={"configurable": {"session_id": "test_id"}}
    )
    print("AI: ", flush=True, end="")
    for content in response:
        print(content, flush=True, end="")
    print("")

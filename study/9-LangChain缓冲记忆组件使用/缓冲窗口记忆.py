from operator import itemgetter
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import MoonshotChat
import os
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

load_dotenv()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是Moonshot的聊天机器人，请根据对应的上下文回答用户问题"),
        MessagesPlaceholder("history"),
        ("human", "{query}"),
    ]
)

chat = MoonshotChat(moonshot_api_key=os.getenv("OPENAI_API_KEY"))
memory = ConversationBufferWindowMemory(k=2, return_messages=True)

chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables)
        | itemgetter(memory.memory_key)
    )
    | prompt
    | chat
    | StrOutputParser()
)

while True:
    query = input("Human: ")
    if query == "q":
        exit(0)

    chain_input = {"query": query}
    res = chain.stream(chain_input)

    print("AI: ", flush=True, end="")
    content = ""
    for chunk in res:
        content += chunk
        print(chunk, flush=True, end="")
    memory.save_context(chain_input, {"output": content})
    print("")
    print("history:", memory.load_memory_variables({}))

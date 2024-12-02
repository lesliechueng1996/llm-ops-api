from langchain_core.prompts import ChatPromptTemplate

system_chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个聊天机器人, 请回复我的问题，我叫{username}"),
    ]
)
human_chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{query}"),
    ]
)

chat_prompt = system_chat_prompt + human_chat_prompt
print(chat_prompt)

chat_prompt_value = chat_prompt.invoke({"username": "Leslie", "query": "你好"})
print(chat_prompt_value)

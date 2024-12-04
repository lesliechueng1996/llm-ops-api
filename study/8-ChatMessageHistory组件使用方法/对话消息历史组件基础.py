from langchain_core.chat_history import InMemoryChatMessageHistory

chat_history = InMemoryChatMessageHistory()

chat_history.add_user_message("你好")
chat_history.add_ai_message("你好, 你有什么问题吗?")
print(chat_history.messages)

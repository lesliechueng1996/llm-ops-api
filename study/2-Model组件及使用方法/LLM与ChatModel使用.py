from datetime import datetime
from dotenv import load_dotenv
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.prompts import ChatPromptTemplate
import os

load_dotenv()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是 Moonshot 开发的聊天机器人，请回答用户的问题，现在的时间是{now}",
        ),
        ("human", "{query}"),
    ]
).partial(now=datetime.now())

chat = MoonshotChat(moonshot_api_key=os.getenv("OPENAI_API_KEY"))

ai_message = chat.invoke(prompt.invoke({"query": "现在几点，请讲一个程序员的笑话"}))

print(ai_message.type)
print("====================")
print(ai_message.content)
print("====================")
print(ai_message.response_metadata)

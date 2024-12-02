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

ai_messages = chat.batch(
    [
        prompt.invoke({"query": "你好，你是?"}),
        prompt.invoke({"query": "请讲一个程序员的冷笑话"}),
    ]
)
for ai_message in ai_messages:
    print(ai_message.content)
    print("====================")

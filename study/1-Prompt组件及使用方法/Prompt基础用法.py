"""
@Time   : 2024/12/02 20:03
@Author : Leslie
@File   : Prompt基础用法.py
"""

from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import AIMessage
from datetime import datetime

prompt = PromptTemplate.from_template("请讲一个关于{subject}的笑话")
print(prompt)
print(prompt.format(subject="程序员"))
prompt_value = prompt.invoke({"subject": "程序员"})
print(prompt_value)
print(prompt_value.to_string())
print(prompt_value.to_messages())

print("==========")

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个聊天机器人, 当前时间为: {now}"),
        MessagesPlaceholder("chat_history"),
        HumanMessagePromptTemplate.from_template("请讲一个关于{subject}的笑话"),
    ]
).partial(now=datetime.now())
print(chat_prompt)
chat_prompt_value = chat_prompt.invoke(
    {
        "chat_history": [
            ("human", "你好"),
            AIMessage("你好"),
        ],
        "subject": "程序员",
    }
)
print(chat_prompt_value)
print(chat_prompt_value.to_string())
print(chat_prompt_value.to_messages())

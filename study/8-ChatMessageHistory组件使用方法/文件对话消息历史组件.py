from dotenv import load_dotenv
from openai import OpenAI
from os import getenv
from langchain_community.chat_message_histories import FileChatMessageHistory

load_dotenv()

client = OpenAI(api_key=getenv("OPENAI_API_KEY"), base_url=getenv("OPENAI_URL"))
chat_history = FileChatMessageHistory(
    "./study/8-ChatMessageHistory组件使用方法/memory.txt"
)

while True:
    query = input("Human: ")
    if query == "q":
        break

    system_prompt = f"""你是聊天机器人，可以根据相应的上下文回复用户信息，上下文里存放的是人类与你对话的消息记录
    <context>
    {chat_history}
    </context>
"""

    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        stream=True,
    )

    print("AI: ", flush=True, end="")
    content = ""
    for message in response:
        temp = message.choices[0].delta.content
        if temp is None:
            break
        print(temp, flush=True, end="")
        content += temp
    print("")
    chat_history.add_user_message(query)
    chat_history.add_ai_message(content)

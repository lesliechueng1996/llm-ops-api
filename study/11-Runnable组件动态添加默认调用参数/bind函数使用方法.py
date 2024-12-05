from dotenv import load_dotenv
from os import getenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "目前正在进行一项测试，你只需要返回用户的输入即可，不要回复其他任何内容",
        ),
        ("human", "{query}"),
    ]
)

chat = MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), model="moonshot-v1-8k")

# bind 可以覆盖原有的参数
chain = prompt | chat.bind(model="moonshot-v1-32k") | StrOutputParser()

content = chain.invoke({"query": "你好，世界"})
print(content)

from dotenv import load_dotenv
from os import getenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import MoonshotChat, QianfanChatEndpoint
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.utils import ConfigurableField

load_dotenv()

prompt = ChatPromptTemplate.from_template("{query}")
chat = ChatOpenAI().configurable_alternatives(
    ConfigurableField("llm"),
    default_key="gpt",
    moon=MoonshotChat(
        moonshot_api_key=getenv("OPENAI_API_KEY"), model="moonshot-v1-8k"
    ),
    qianfan=QianfanChatEndpoint(),
)
chain = prompt | chat | StrOutputParser()

content = chain.invoke({"query": "你是谁?"}, config={"configurable": {"llm": "moon"}})
print(content)

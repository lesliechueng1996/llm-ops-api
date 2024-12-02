from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.output_parsers.string import StrOutputParser
from dotenv import load_dotenv
import os
from typing import Any

load_dotenv()

prompt = ChatPromptTemplate.from_template("{query}")
chat = MoonshotChat(moonshot_api_key=os.getenv("OPENAI_API_KEY"))
parser = StrOutputParser()

chain = prompt | chat | parser

content = chain.invoke({"query": "你好，你是谁？"})
print(content)

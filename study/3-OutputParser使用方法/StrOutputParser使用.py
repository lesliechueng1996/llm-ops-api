from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from dotenv import load_dotenv
import os

load_dotenv()

prompt = ChatPromptTemplate.from_template("{query}")

chat = MoonshotChat(moonshot_api_key=os.getenv("OPENAI_API_KEY"))

output_parser = StrOutputParser()
content = output_parser.invoke(
    chat.invoke(prompt.invoke({"query": "你好, 请问你是谁？"}))
)
print(content)

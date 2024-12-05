from dotenv import load_dotenv
from os import getenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import MoonshotChat, QianfanChatEndpoint
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

prompt = ChatPromptTemplate.from_template("{query}")
chat = QianfanChatEndpoint().with_fallbacks(
    [MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"))]
)
chain = prompt | chat | StrOutputParser()

print(chain.invoke("你是谁?"))

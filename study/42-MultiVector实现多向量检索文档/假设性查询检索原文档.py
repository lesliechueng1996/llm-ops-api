from os import getenv
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter

load_dotenv()


class HypotheticalQuestion(BaseModel):
    questions: List[str] = Field(
        description="假设性问题，类型为字符串列表",
    )


prompt = ChatPromptTemplate.from_template(
    "生成一个包含3个假设性问题的列表，这些问题可以用于回答下面的文档：\n\n{doc}"
)

chat = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
)

structured_chat = chat.with_structured_output(HypotheticalQuestion)

chain = {"doc": lambda x: x.page_content} | prompt | structured_chat

hypothetical_questions: HypotheticalQuestion = chain.invoke(
    Document(page_content="我叫慕小课，我喜欢打篮球，游泳，看书。")
)
print(hypothetical_questions)

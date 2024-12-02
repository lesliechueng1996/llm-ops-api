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


class Chain:
    steps: list = []

    def __init__(self, steps: list) -> None:
        self.steps = steps

    def invoke(self, input: Any) -> Any:
        for step in self.steps:
            input = step.invoke(input)
            print(step)
            print(input)
            print("=====")
        return input


chain = Chain([prompt, chat, parser])
content = chain.invoke({"query": "你好，你是谁？"})
print(content)

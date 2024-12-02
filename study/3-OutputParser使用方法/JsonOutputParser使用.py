from pydantic import BaseModel, Field
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from dotenv import load_dotenv
import os

load_dotenv()


class Joke(BaseModel):
    joke: str = Field(description="笑话")
    laughing_point: str = Field(description="笑点")


json_parser = JsonOutputParser(pydantic_object=Joke)
print(json_parser.get_format_instructions())
print("====================")

prompt = ChatPromptTemplate.from_template(
    "请根据用户的提问进行回答。\n{format_instructions}\n{query}"
).partial(format_instructions=json_parser.get_format_instructions())

chat = MoonshotChat(moonshot_api_key=os.getenv("OPENAI_API_KEY"))
result = json_parser.invoke(chat.invoke(prompt.invoke({"query": "讲一个程序员的笑话"})))
print(result)
print(type(result))

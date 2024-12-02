from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables import RunnableParallel
from dotenv import load_dotenv
import os

load_dotenv()

joke_prompt = ChatPromptTemplate.from_template("请帮我写一个关于{subject}的笑话")
poem_prompt = ChatPromptTemplate.from_template("请帮我写一首关于{subject}的诗")

chat = MoonshotChat(moonshot_api_key=os.getenv("OPENAI_API_KEY"))

str_parser = StrOutputParser()

joke_chain = joke_prompt | chat | str_parser
poem_chain = poem_prompt | chat | str_parser

# map_chain = RunnableParallel({"joke": joke_chain, "poem": poem_chain})
map_chain = RunnableParallel(joke=joke_chain, poem=poem_chain)

content = map_chain.invoke({"subject": "猫"})
print(content)

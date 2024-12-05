from os import getenv
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.utils import ConfigurableField

load_dotenv()

prompt = ChatPromptTemplate.from_template("请生成一个{x}以下的随机数")

# bind 函数只能配置 invoke 使用的参数，无法配置组件的配置参数
chat = MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY")).configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature",
    )
)

chain = prompt | chat | StrOutputParser()

# content = chain.invoke({"x": 10}, config={"configurable": {"llm_temperature": "0"}})

chain_with_config = chain.with_config(configurable={"llm_temperature": "0"})
content = chain_with_config.invoke({"x": 10})
print(content)

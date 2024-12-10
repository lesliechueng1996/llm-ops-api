from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from os import getenv
from langchain_community.tools.openai_dalle_image_generation import (
    OpenAIDALLEImageGenerationTool,
)
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


google_serper = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具传递的参数是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)


class DallEArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


dalle = OpenAIDALLEImageGenerationTool(
    api_wrapper=DallEAPIWrapper(
        model="dall-e-3",
        api_key=SecretStr(getenv("OPENAI_KEY")),
        base_url=getenv("OPENAI_API_URL"),
    ),
    args_schema=DallEArgsSchema,
)

tools = [google_serper, dalle]
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是由OpenAI开发的聊天机器人，善于帮助用户解决问题。",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
)

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print(agent_executor.invoke({"input": "马拉松的世界纪录是多少？"}))

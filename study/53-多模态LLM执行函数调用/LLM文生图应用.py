from dotenv import load_dotenv
from os import getenv
from langchain_community.tools.openai_dalle_image_generation import (
    OpenAIDALLEImageGenerationTool,
)
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


load_dotenv()

dalle = OpenAIDALLEImageGenerationTool(
    api_wrapper=DallEAPIWrapper(
        model="dall-e-3",
        api_key=SecretStr(getenv("OPENAI_KEY")),
        base_url=getenv("OPENAI_API_URL"),
    )
)

llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
)
llm_with_tools = llm.bind_tools([dalle], tool_choice="openai_dalle")

chain = llm_with_tools | (lambda msg: msg.tool_calls[0]["args"]) | dalle
print(chain.invoke("帮我绘制一张公司裁员的图片，要求灰色调，氛围悲凉。"))

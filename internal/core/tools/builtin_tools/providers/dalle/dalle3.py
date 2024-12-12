"""
@Time   : 2024/12/12 18:20
@Author : Leslie
@File   : dalle3.py
"""

from langchain_community.tools.openai_dalle_image_generation import (
    OpenAIDALLEImageGenerationTool,
)
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from pydantic import SecretStr, BaseModel, Field
from os import getenv
from langchain_core.tools import BaseTool
from internal.lib import add_attribute


class Dalle3ArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


@add_attribute("args_schema", Dalle3ArgsSchema)
def dalle3(**kwargs) -> BaseTool:
    dalle = OpenAIDALLEImageGenerationTool(
        api_wrapper=DallEAPIWrapper(
            model="dall-e-3",
            api_key=SecretStr(getenv("OPENAI_KEY")),
            base_url=getenv("OPENAI_API_URL"),
            **kwargs,
        )
    )
    return dalle

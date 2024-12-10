import requests
import json
from os import getenv
from dotenv import load_dotenv
from typing import Any, Dict, Optional, Type, TypedDict
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, render_text_description_and_args
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableConfig
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的目标城市，例如：北京")


class GaodeWeatherTool(BaseTool):
    name: str = "gaode_weather"
    description: str = "当你想查询天气或者与天气相关的问题时可以使用的工具"
    args_schema: Type[BaseModel] = GaodeWeatherArgsSchema

    def _run(self, city: str) -> str:
        gaode_api_key = getenv("GAODE_API_KEY")
        if not gaode_api_key:
            return "请先配置高德地图的API Key"
        try:
            api_base_url = "https://restapi.amap.com/v3"
            session = requests.session()

            city_response = session.request(
                method="GET",
                url=f"{api_base_url}/config/district?key={gaode_api_key}&keywords={city}&subdistrict=0",
            )
            city_response.raise_for_status()
            city_data = city_response.json()
            if city_data.get("info") != "OK":
                raise Exception("无法获取城市信息")
            city_adcode = city_data.get("districts")[0].get("adcode")

            weather_response = session.request(
                method="GET",
                url=f"{api_base_url}/weather/weatherInfo?key={gaode_api_key}&city={city_adcode}&extensions=all",
            )
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            if weather_data.get("info") != "OK":
                raise Exception("无法获取天气信息")
            return json.dumps(weather_data)
        except Exception as e:
            print(e)
            return f"获取{city}天气预报信息失败"


gaode_weather_tool = GaodeWeatherTool()
google_serper_tool = GoogleSerperRun(
    name="google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具传递的参数是搜索查询语句。"
    ),
    args_schema=GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)

tool_dict = {
    gaode_weather_tool.name: gaode_weather_tool,
    google_serper_tool.name: google_serper_tool,
}
tool_list = [gaode_weather_tool, google_serper_tool]


class ToolCallRequest(TypedDict):
    name: str
    arguments: Dict[str, Any]


def invoke_tool(req: ToolCallRequest, config: Optional[RunnableConfig]) -> str:
    tool_name = req["name"]
    tool = tool_dict.get(tool_name)
    return tool.invoke(req["arguments"], config)


system_prompt = """你是一个聊天机器人，可以访问以下一组工具。
以下是每个工具的名称和描述

{rendered_tools}

根据用户输入，返回要使用的工具的名称和输入。
将您的响应作为具有`name`和`arguments`键的JSON块返回。
`arguments`应该是一个字典，其中键对应于参数名称，值对应于请求的值。
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{query}"),
    ]
).partial(rendered_tools=render_text_description_and_args(tool_list))

llm = MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), temperature=0)

chain = (
    {"query": RunnablePassthrough()}
    | prompt
    | llm
    | JsonOutputParser()
    | RunnablePassthrough.assign(output=invoke_tool)
)

print(chain.invoke("马拉松的世界纪录是多少？"))

import requests
import json
from os import getenv
from dotenv import load_dotenv
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import ToolMessage

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

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是由OpenAI开发的聊天机器人，可以帮助用户回答问题，必要时刻请调用工具帮助用户解答。",
        ),
        ("human", "{query}"),
    ]
)

llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
)
llm_with_tool = llm.bind_tools(tools=tool_list)
chain = {"query": RunnablePassthrough()} | prompt | llm_with_tool

# query = "沈阳现在天气怎么样，有什么合适穿的衣服呢？"
query = "马拉松的世界纪录是多少？"
resp = chain.invoke(query)
tool_calls = resp.tool_calls

if len(tool_calls) <= 0:
    print("生成内容: ", resp.content)
else:
    messages = prompt.invoke(query).to_messages()
    messages.append(resp)

    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args")
        tool = tool_dict.get(tool_name)
        print(f"调用工具: {tool_name}")
        content = tool.invoke(tool_args)
        print(f"工具返回: {content}")
        tool_call_id = tool_call.get("id")

        messages.append(
            ToolMessage(
                content=content,
                tool_call_id=tool_call_id,
            )
        )

    print("生成内容: ", llm.invoke(messages))

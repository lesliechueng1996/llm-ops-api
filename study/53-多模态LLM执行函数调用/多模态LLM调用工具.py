import requests
import json
from os import getenv
from dotenv import load_dotenv
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


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


tool = GaodeWeatherTool()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            [
                {"type": "text", "text": "请获取下面图片所在城市的天气预报。"},
                {"type": "image_url", "image_url": {"url": "{image_url}"}},
            ],
        )
    ]
)
weather_prompt = ChatPromptTemplate.from_template(
    """请整理传递的城市的天气预报信息，并以用户友好的格式输出。
                                                  
<weather>
{weather}
</weather>"""
)

llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
    temperature=0,
)
llm_with_tools = llm.bind_tools([tool])

chain = (
    {
        "weather": (
            {
                "image_url": RunnablePassthrough(),
            }
            | prompt
            | llm_with_tools
            | (lambda x: x.tool_calls[0]["args"])
            | tool
        )
    }
    | weather_prompt
    | llm
    | StrOutputParser()
)

print(
    chain.invoke(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Canton_Tower_20241027.jpg/278px-Canton_Tower_20241027.jpg"
    )
)

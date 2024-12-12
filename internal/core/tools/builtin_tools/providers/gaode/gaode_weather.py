"""
@Time   : 2024/12/12 18:54
@Author : Leslie
@File   : gaode_weather.py
"""

import requests
import json
from os import getenv
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from internal.lib.helper import add_attribute


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


@add_attribute("args_schema", GaodeWeatherArgsSchema)
def gaode_weather(**kwargs) -> BaseTool:
    return GaodeWeatherTool()

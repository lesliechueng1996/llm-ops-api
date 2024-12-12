"""
@Time   : 2024/12/12 18:59
@Author : Leslie
@File   : gaode_ip.py
"""

from os import getenv
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type

import requests


class GaodeIPArgsSchema(BaseModel):
    ip: str = Field(description="需要查询所在地的IP地址，例如：114.247.50.2")


class GaodeIPTool(BaseTool):
    name: str = "gaode_ip"
    description: str = "当你想查询ip所在地址的问题时可以使用的工具"
    args_schema: Type[BaseModel] = GaodeIPArgsSchema

    def _run(self, ip: str) -> str:
        gaode_api_key = getenv("GAODE_API_KEY")
        if not gaode_api_key:
            return "请先配置高德地图的API Key"

        try:
            api_base_url = "https://restapi.amap.com/v3"
            session = requests.session()

            ip_response = session.request(
                method="GET",
                url=f"{api_base_url}/ip?key={gaode_api_key}&ip={ip}",
            )
            ip_response.raise_for_status()
            ip_data = ip_response.json()
            if ip_data.get("info") != "OK":
                raise Exception("无法获取所在城市信息")
            ip_province = ip_data.get("province")
            ip_city = ip_data.get("city")
            if ip_province == ip_city:
                return ip_city
            return ip_province + ip_city
        except Exception as e:
            print(e)
            return f"获取{ip}所在地失败"


def gaode_ip(**kwargs) -> BaseTool:
    return GaodeIPTool()

"""
@Time   : 2024/12/12 19:14
@Author : Leslie
@File   : wikipedia_search.py
"""

from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import BaseTool


def wikipedia_search(**kwargs) -> BaseTool:
    return WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(),
    )

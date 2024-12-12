"""
@Time   : 2024/12/12 19:14
@Author : Leslie
@File   : wikipedia_search.py
"""

from langchain_community.tools.wikipedia.tool import (
    WikipediaQueryRun,
    WikipediaQueryInput,
)
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import BaseTool

from internal.lib.helper import add_attribute


@add_attribute("args_schema", WikipediaQueryInput)
def wikipedia_search(**kwargs) -> BaseTool:
    return WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(),
    )

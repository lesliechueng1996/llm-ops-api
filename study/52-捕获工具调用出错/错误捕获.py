from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

load_dotenv()


@tool
def complex_tool(int_arg: int, float_arg: float, dict_arg: dict) -> float:
    """使用复杂工具进行复杂计算操作"""
    return int_arg * float_arg


llm = ChatOpenAI(
    api_key=getenv("OPENAI_KEY"),
    base_url=getenv("OPENAI_API_URL"),
    model="gpt-4o-mini",
    temperature=0,
)

llm_with_tools = llm.bind_tools([complex_tool])


def try_except_tool(tool_args: dict, config: RunnableConfig):
    try:
        return complex_tool.invoke(tool_args, config=config)
    except Exception as e:
        return (
            f"调用工具时使用以下参数:\n\n{tool_args}\n\n引发以下错误:\n\n{type(e)}: {e}"
        )


chain = llm_with_tools | (lambda x: x.tool_calls[0]["args"]) | try_except_tool

print(chain.invoke("使用复杂工具，对应参数为5和2.1"))

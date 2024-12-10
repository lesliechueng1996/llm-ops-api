from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig, Runnable
from langchain_core.messages import AIMessage, ToolCall, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class CustomToolException(Exception):
    tool_call: ToolCall
    exception: Exception

    def __init__(self, tool_call: ToolCall, exception):
        super().__init__()
        self.tool_call = tool_call
        self.exception = exception


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

llm_with_tools = llm.bind_tools(tools=[complex_tool], tool_choice="complex_tool")

prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{query}"),
        ("placeholder", "{last_output}"),
    ]
)


def exception_to_msg(inputs: dict):
    exception: CustomToolException = inputs.pop("exception")
    messages = [
        AIMessage(content="", tool_calls=[exception.tool_call]),
        ToolMessage(
            content=str(exception.exception), tool_call_id=exception.tool_call["id"]
        ),
        HumanMessage(
            content="最后一次工具调用引发了异常，请尝试使用更正的参数再次调用该工具，请不要重复犯错。"
        ),
    ]
    inputs["last_output"] = messages
    return inputs


def try_except_tool(msg: AIMessage, config: RunnableConfig):
    try:
        return complex_tool.invoke(msg.tool_calls[0]["args"], config=config)
    except Exception as e:
        raise CustomToolException(msg.tool_calls[0], e)


chain: Runnable = prompt | llm_with_tools | try_except_tool
self_correcting_chain = chain.with_fallbacks(
    fallbacks=[exception_to_msg | chain], exception_key="exception"
)

print(self_correcting_chain.invoke({"query": "使用复杂工具，对应参数为5和2.1"}))

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class MultiplyInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


@tool("multiply_tool", return_direct=True, args_schema=MultiplyInput)
def multiply(a: int, b: int) -> int:
    """将传递的两个数字相乘"""
    return a * b


print(f"名称：{multiply.name}")
print(f"描述：{multiply.description}")
print(f"参数：{multiply.args}")
print(f"是否直接返回：{multiply.return_direct}")
print(f"调用：{multiply.invoke({'a': 2, 'b': 3})}")

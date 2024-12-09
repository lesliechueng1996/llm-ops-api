from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class MultiplyInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


def multiply(a: int, b: int) -> int:
    return a * b


def amultiply(a: int, b: int) -> int:
    return a * b


calculator = StructuredTool.from_function(
    func=multiply,
    coroutine=amultiply,
    name="multiply_tool",
    description="将传递的两个数字相乘",
    args_schema=MultiplyInput,
    return_direct=True,
)

print(f"名称：{calculator.name}")
print(f"描述：{calculator.description}")
print(f"参数：{calculator.args}")
print(f"是否直接返回：{calculator.return_direct}")
print(f"调用：{calculator.invoke({'a': 2, 'b': 3})}")

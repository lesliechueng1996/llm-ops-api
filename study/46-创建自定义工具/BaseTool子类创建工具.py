from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class MultiplyInput(BaseModel):
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


class MultiplyTool(BaseTool):
    name: str = "multiply_tool"
    description: str = "将传递的两个数字相乘"
    args_schema: Type[BaseModel] = MultiplyInput
    return_direct: bool = True

    def _run(self, a: int, b: int) -> int:
        return a * b


calculator = MultiplyTool()
print(f"名称：{calculator.name}")
print(f"描述：{calculator.description}")
print(f"参数：{calculator.args}")
print(f"是否直接返回：{calculator.return_direct}")
print(f"调用：{calculator.invoke({'a': 2, 'b': 3})}")

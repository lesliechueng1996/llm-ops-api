"""
@Time   : 2024/12/02 20:29
@Author : Leslie
@File   : Prompt拼接.py
"""

from langchain_core.prompts import PromptTemplate

prompt = (
    PromptTemplate.from_template("请讲一个关于{subject}的笑话")
    + ",让我开心一下"
    + "\n使用{language}"
)
print(prompt)
prompt_value = prompt.invoke({"subject": "程序员", "language": "中文"})
print(prompt_value)
print(prompt_value.to_string())
print(prompt_value.to_messages())

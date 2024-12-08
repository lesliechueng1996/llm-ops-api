from dotenv import load_dotenv
from os import getenv
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{question}"),
        ("ai", "{answer}"),
    ]
)
examples = [
    {"question": "帮我计算下2+2等于多少", "answer": "4"},
    {"question": "帮我计算下2+3等于多少", "answer": "5"},
    {"question": "帮我计算下20*15等于多少", "answer": "300"},
]

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

print(f"少量示例模板: {few_shot_prompt.format()}")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个可以计算复杂数学问题的聊天机器人"),
        few_shot_prompt,
        ("human", "{question}"),
    ]
)

chain = (
    prompt
    | MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), temperature=0)
    | StrOutputParser()
)
print(chain.invoke({"question": "帮我计算下2*5等于多少"}))

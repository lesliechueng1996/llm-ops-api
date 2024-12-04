from typing import Tuple
from dotenv import load_dotenv
from os import getenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter
import tiktoken

load_dotenv()


# To fix "NotImplementedError: get_num_tokens_from_messages() is not presently implemented for model cl100k_base" issue
class CustomMoonshotChat(MoonshotChat):
    def _get_encoding_model(self) -> Tuple[str, tiktoken.Encoding]:
        model = "gpt-3.5-turbo"
        return model, tiktoken.encoding_for_model(model)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是Moonshot的聊天机器人，请根据对应的上下文回答用户问题"),
        MessagesPlaceholder("history"),
        ("human", "{query}"),
    ]
)

client = CustomMoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"))
memory = ConversationSummaryBufferMemory(
    max_token_limit=300,
    llm=CustomMoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY")),
    return_messages=True,
)

chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables)
        | itemgetter(memory.memory_key)
    )
    | prompt
    | client
    | StrOutputParser()
)

while True:
    query = input("Human: ")
    if query == "q":
        exit(0)

    chain_input = {"query": query}
    res = chain.stream(chain_input)

    print("AI: ", flush=True, end="")
    content = ""
    for chunk in res:
        content += chunk
        print(chunk, flush=True, end="")
    print("")
    memory.save_context(chain_input, {"output": content})
    print("history: ", memory.load_memory_variables({}))

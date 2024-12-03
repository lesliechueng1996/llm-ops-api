import time
from typing import Any
from uuid import UUID
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk, LLMResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class LLMOpsCallbackHandler(BaseCallbackHandler):
    start_time: float = 0

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any
    ) -> Any:
        print("聊天模型开始")
        print("serialized", serialized)
        print("messages", messages)
        self.start_time = time.time()

    # def on_llm_new_token(
    #     self,
    #     token: str,
    #     *,
    #     chunk: GenerationChunk | ChatGenerationChunk | None = None,
    #     run_id: UUID,
    #     parent_run_id: UUID | None = None,
    #     **kwargs: Any
    # ) -> Any:
    #     print("新的token", token)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any
    ) -> Any:
        print("聊天模型结束")
        print("response", response)
        print("耗时", time.time() - self.start_time)


prompt = ChatPromptTemplate.from_template("{query}")
chat = MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"))
parser = StrOutputParser()

chain = {"query": RunnablePassthrough()} | prompt | chat | parser

content = chain.invoke(
    "你好，你是?",
    config={"callbacks": [StdOutCallbackHandler(), LLMOpsCallbackHandler()]},
)
print(content)

# res = chain.stream(
#     "你好，你是?",
#     config={"callbacks": [StdOutCallbackHandler(), LLMOpsCallbackHandler()]},
# )
# for i in res:
#     pass

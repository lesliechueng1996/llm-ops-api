from typing import List
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document


class CustomRetriever(BaseRetriever):
    documents: List[Document]
    k: int

    def _get_relevant_documents(self, query: str, *, run_manager):
        matching_docs = []
        for doc in self.documents:
            if len(matching_docs) >= self.k:
                return matching_docs
            if query.lower() in doc.page_content.lower():
                matching_docs.append(doc)
        return matching_docs


documents = [
    Document(page_content="笨笨是一只很喜欢睡觉的猫咪", metadata={"page": 1}),
    Document(page_content="我喜欢在夜晚听音乐，这让我感到放松。", metadata={"page": 2}),
    Document(page_content="猫咪在窗台上打盹，看起来非常可爱。", metadata={"page": 3}),
    Document(page_content="学习新技能是每个人都应该追求的目标。", metadata={"page": 4}),
    Document(
        page_content="我最喜欢的食物是意大利面，尤其是番茄酱的那种。",
        metadata={"page": 5},
    ),
    Document(
        page_content="昨晚我做了一个奇怪的梦，梦见自己在太空飞行。",
        metadata={"page": 6},
    ),
    Document(page_content="我的手机突然关机了，让我有些焦虑。", metadata={"page": 7}),
    Document(
        page_content="阅读是我每天都会做的事情，我觉得很充实。", metadata={"page": 8}
    ),
    Document(
        page_content="他们一起计划了一次周末的野餐，希望天气能好。",
        metadata={"page": 9},
    ),
    Document(page_content="我的狗喜欢追逐球，看起来非常开心。", metadata={"page": 10}),
]

retriever = CustomRetriever(
    documents=documents,
    k=3,
)

results = retriever.invoke("猫")
for result in results:
    print(result.page_content)
    print("===================")

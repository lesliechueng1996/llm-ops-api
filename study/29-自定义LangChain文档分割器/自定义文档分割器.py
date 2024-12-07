from typing import List
import jieba.analyse
from langchain_text_splitters import TextSplitter
from langchain_unstructured import UnstructuredLoader


class CustomTextSplitter(TextSplitter):
    def __init__(self, seperator: str, top_k: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.seperator = seperator
        self.top_k = top_k

    def split_text(self, text: str) -> List[str]:
        texts = text.split(self.seperator)

        text_keywords = []
        for split_text in texts:
            keywords = jieba.analyse.extract_tags(split_text, self.top_k)
            text_keywords.append(keywords)

        return [",".join(keywords) for keywords in text_keywords]


loader = UnstructuredLoader("./study/28-语义文档分割器与其他内容分割器/科幻短篇.txt")
splitter = CustomTextSplitter(seperator="\n\n", top_k=10)

chunks = splitter.split_documents(loader.load())

for chunk in chunks:
    print(chunk.page_content)

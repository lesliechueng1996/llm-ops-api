from langchain_unstructured.document_loaders import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken


def calculate_token_count(query: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-3.5")
    return len(encoding.encode(query))


loader = UnstructuredLoader("./study/28-语义文档分割器与其他内容分割器/科幻短篇.txt")
separators = ["\n\n", "\n", "。|！|？", "\.\s|\!\s|\?\s", "；|;\s", "，|,\s", " ", ""]
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
    length_function=calculate_token_count,
    separators=separators,
    is_separator_regex=True,
)

chunks = splitter.split_documents(loader.load())
for chunk in chunks:
    print(f"块内容大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

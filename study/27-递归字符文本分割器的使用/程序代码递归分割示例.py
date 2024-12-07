from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

loader = UnstructuredFileLoader("./study/27-递归字符文本分割器的使用/demo.py")
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

docs = loader.load()
chunks = splitter.split_documents(docs)
for chunk in chunks:
    print(f"块内容大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

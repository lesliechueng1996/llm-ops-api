from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = UnstructuredMarkdownLoader(
    file_path="./study/23-LangChain内置文档加载器使用/项目API资料.md",
)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

docs = loader.load()
chunks = splitter.split_documents(docs)
for chunk in chunks:
    print(f"块内容大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

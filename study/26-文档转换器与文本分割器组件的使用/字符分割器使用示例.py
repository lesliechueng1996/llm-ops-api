from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader

splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

loader = UnstructuredMarkdownLoader(
    file_path="./study/23-LangChain内置文档加载器使用/项目API资料.md",
)

docs = loader.load()
chunks = splitter.split_documents(docs)
for chunk in chunks:
    print(f"块内容大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

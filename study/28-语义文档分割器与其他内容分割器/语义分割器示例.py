from dotenv import load_dotenv
from langchain_unstructured.document_loaders import UnstructuredLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

load_dotenv()

loader = UnstructuredLoader("./study/28-语义文档分割器与其他内容分割器/科幻短篇.txt")
splitter = SemanticChunker(
    embeddings=QianfanEmbeddingsEndpoint(),
    add_start_index=True,
    number_of_chunks=10,
    sentence_split_regex=r"(?<=[。？！])",
)

chunks = splitter.split_documents(loader.load())
for chunk in chunks:
    print(f"块内容大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

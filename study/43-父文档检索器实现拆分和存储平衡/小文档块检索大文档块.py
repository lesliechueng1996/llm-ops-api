from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_weaviate import WeaviateVectorStore
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
from os import getenv
from langchain.storage import LocalFileStore

load_dotenv()

doc_paths = [
    "./study/22-Document组件与文档加载器/电商产品数据.txt",
    "./study/23-LangChain内置文档加载器使用/项目API资料.md",
]

loaders = [UnstructuredFileLoader(path) for path in doc_paths]

docs = []
for loader in loaders:
    docs.extend(loader.load())

print(len(docs))

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

db_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=getenv("WEAVIATE_CLOUD_HOST"),
    auth_credentials=Auth.api_key(getenv("WEAVIATE_CLOUD_API_KEY")),
    skip_init_checks=True,
)

vector_store = WeaviateVectorStore(
    client=db_client,
    text_key="text",
    embedding=HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2"
    ),
    index_name="ParentDocument",
)

file_store = LocalFileStore(
    "./study/43-父文档检索器实现拆分和存储平衡/parent-document/"
)
parent_doc_retriever = ParentDocumentRetriever(
    vectorstore=vector_store,
    byte_store=file_store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
parent_doc_retriever.add_documents(docs, ids=None)

search_docs = parent_doc_retriever.invoke("分享关于LLMOps的一些应用配置")
print(search_docs)
print(len(search_docs))

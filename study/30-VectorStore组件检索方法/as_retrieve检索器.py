from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate.vectorstores import WeaviateVectorStore
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
from os import getenv
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

load_dotenv()

file_path = "./study/23-LangChain内置文档加载器使用/项目API资料.md"
loader = UnstructuredMarkdownLoader(file_path)

separators = ["\n\n", "\n", "。|！|？", "\.\s|\!\s|\?\s", "；|;\s", "，|,\s", " ", ""]
splitter = RecursiveCharacterTextSplitter(
    separators=separators,
    chunk_size=500,
    chunk_overlap=50,
    is_separator_regex=True,
    add_start_index=True,
)

docs = loader.load()
chunks = splitter.split_documents(docs)

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=getenv("WEAVIATE_CLOUD_HOST"),
    auth_credentials=Auth.api_key(getenv("WEAVIATE_CLOUD_API_KEY")),
    skip_init_checks=True,
)
vector_store = WeaviateVectorStore(
    client=client,
    text_key="text",
    embedding=QianfanEmbeddingsEndpoint(),
    index_name="DatasetDemo",
)

vector_store.add_documents(chunks)

retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.5},
)

results = retriever.invoke("关于配置接口的信息有哪些")

print(list(document.page_content[:50] for document in results))
print(len(results))
client.close()

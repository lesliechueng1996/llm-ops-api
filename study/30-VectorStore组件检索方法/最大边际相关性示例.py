from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate.vectorstores import WeaviateVectorStore
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
from os import getenv

# from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_openai.embeddings import OpenAIEmbeddings

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
    embedding=OpenAIEmbeddings(
        api_key=getenv("OPENAI_KEY"),
        base_url=getenv("OPENAI_API_URL"),
        model="text-embedding-3-small",
    ),
    index_name="DatasetDemo",
)

vector_store.add_documents(chunks)

# results = vector_store.similarity_search("关于配置接口的信息有哪些")

#  排除重复的结果，保证结果多样性
results = vector_store.max_marginal_relevance_search("关于配置接口的信息有哪些")

for result in results:
    print(result.page_content[:100])
    print("===================")
client.close()

from os import getenv
from dotenv import load_dotenv
from uuid import uuid4
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import MoonshotChat
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_core.documents import Document
from langchain.storage import LocalFileStore
from langchain.retrievers import MultiVectorRetriever

load_dotenv()

file_path = "./study/22-Document组件与文档加载器/电商产品数据.txt"
file_loader = UnstructuredLoader(file_path)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = file_loader.load_and_split(splitter)

prompt = ChatPromptTemplate.from_template("请总结以下文档的内容：\n\n{doc}")
chat = MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY")).with_fallbacks(
    [
        ChatOpenAI(
            api_key=getenv("OPENAI_KEY"),
            base_url=getenv("OPENAI_API_URL"),
            model="gpt-4o-mini",
        )
    ]
)
chain = {"doc": lambda x: x.page_content} | prompt | chat | StrOutputParser()

summaries = chain.with_listeners().batch(
    docs,
    {
        "max_concurrency": 5,
    },
)

ids = [str(uuid4()) for _ in summaries]
summary_docs = [
    Document(page_content=summary, metadata={"doc_id": ids[index]})
    for index, summary in enumerate(summaries)
]

vector_store = FAISS.from_documents(
    documents=summary_docs, embedding=QianfanEmbeddingsEndpoint()
)
file_store = LocalFileStore("./study/42-MultiVector实现多向量检索文档/multi-vector/")

multi_vector_retriever = MultiVectorRetriever(
    vectorstore=vector_store,
    byte_store=file_store,
    id_key="doc_id",
)

multi_vector_retriever.docstore.mset(list(zip(ids, docs)))

search_docs = multi_vector_retriever.invoke("推荐一些潮州特产")
for search_doc in search_docs:
    print(search_doc.page_content[:100])
    print("====================================")

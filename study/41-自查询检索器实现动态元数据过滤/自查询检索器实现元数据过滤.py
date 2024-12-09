from os import getenv
from dotenv import load_dotenv
from langchain.retrievers import SelfQueryRetriever
from langchain_community.chat_models import MoonshotChat
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_core.documents import Document
from langchain.chains.query_constructor.schema import AttributeInfo

load_dotenv()

documents = [
    Document(
        page_content="肖申克的救赎",
        metadata={"year": 1994, "rating": 9.7, "director": "弗兰克·德拉邦特"},
    ),
    Document(
        page_content="霸王别姬",
        metadata={"year": 1993, "rating": 9.6, "director": "陈凯歌"},
    ),
    Document(
        page_content="阿甘正传",
        metadata={"year": 1994, "rating": 9.5, "director": "罗伯特·泽米吉斯"},
    ),
    Document(
        page_content="泰坦尼克号",
        metadat={"year": 1997, "rating": 9.5, "director": "詹姆斯·卡梅隆"},
    ),
    Document(
        page_content="千与千寻",
        metadat={"year": 2001, "rating": 9.4, "director": "宫崎骏"},
    ),
    Document(
        page_content="星际穿越",
        metadat={"year": 2014, "rating": 9.4, "director": "克里斯托弗·诺兰"},
    ),
    Document(
        page_content="忠犬八公的故事",
        metadat={"year": 2009, "rating": 9.4, "director": "莱塞·霍尔斯道姆"},
    ),
    Document(
        page_content="三傻大闹宝莱坞",
        metadat={"year": 2009, "rating": 9.2, "director": "拉库马·希拉尼"},
    ),
    Document(
        page_content="疯狂动物城",
        metadat={"year": 2016, "rating": 9.2, "director": "拜伦·霍华德"},
    ),
    Document(
        page_content="无间道",
        metadat={"year": 2002, "rating": 9.3, "director": "刘伟强"},
    ),
]

attribute_info = [
    AttributeInfo(name="year", description="电影的上映年份", type="integer"),
    AttributeInfo(name="rating", description="电影的评分", type="float"),
    AttributeInfo(name="director", description="电影的导演", type="string"),
]

vector_store = PineconeVectorStore(
    index_name="llmops",
    embedding=HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2"
    ),
    text_key="text",
    namespace="dataset",
)

self_query_retriever = SelfQueryRetriever.from_llm(
    llm=MoonshotChat(moonshot_api_key=getenv("OPENAI_API_KEY"), temperature=0),
    vectorstore=vector_store,
    document_contents="电影的名字",
    metadata_field_info=attribute_info,
    enable_limit=True,
)

# vector_store.add_documents(documents)

results = self_query_retriever.invoke("查找评分高于9.5分的电影")
for result in results:
    print(result)

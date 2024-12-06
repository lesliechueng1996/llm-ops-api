from dotenv import load_dotenv
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

embedding = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

texts = [
    "笨笨是一只很喜欢睡觉的猫咪",
    "我喜欢在夜晚听音乐，这让我感到放松。",
    "猫咪在窗台上打盹，看起来非常可爱。",
    "学习新技能是每个人都应该追求的目标。",
    "我最喜欢的食物是意大利面，尤其是番茄酱的那种。",
    "昨晚我做了一个奇怪的梦，梦见自己在太空飞行。",
    "我的手机突然关机了，让我有些焦虑。",
    "阅读是我每天都会做的事情，我觉得很充实。",
    "他们一起计划了一次周末的野餐，希望天气能好。",
    "我的狗喜欢追逐球，看起来非常开心",
]

metadatas = [
    {"page": 1},
    {"page": 2},
    {"page": 3},
    {"page": 4},
    {"page": 5},
    {"page": 6, "account_id": 1},
    {"page": 7},
    {"page": 8},
    {"page": 9},
    {"page": 10},
]

vector_store = PineconeVectorStore(
    embedding=embedding,
    namespace="dataset",
    index_name="llmops",
)
# vector_store.add_texts(texts=texts, metadatas=metadatas, namespace="dataset")

query = "我养了一只猫，叫笨笨"
print(
    vector_store.similarity_search_with_relevance_scores(
        query,
        # filter={"page": {"$lte": 5}}
        # filter={"$and": [{"page": 5}, {"account_id": 1}]},
        filter={"$or": [{"page": 5}, {"account_id": 1}]},
    )
)

# 删除数据
# id = "5a8565dd-9870-4245-8052-c273be5c0676"
# vector_store.delete([id], namespace="dataset")

# 获取 pinecone 实例
db = vector_store.get_pinecone_index("llmops")

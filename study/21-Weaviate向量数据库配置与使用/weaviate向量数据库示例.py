import weaviate
from weaviate.classes.query import Filter
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

embedding = QianfanEmbeddingsEndpoint()

client = weaviate.connect_to_local()
db = WeaviateVectorStore(
    client=client, index_name="DatasetDemo", text_key="text", embedding=embedding
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

# ids = db.add_texts(texts, metadatas)
# print(ids)

# print(db.similarity_search_with_relevance_scores("我养了一只猫，叫笨笨"))
# print(
#     db.similarity_search_with_relevance_scores(
#         "我养了一只猫，叫笨笨",
#         filters=Filter.by_property("page").greater_or_equal(5),
#     ),
# )

retriever = db.as_retriever()
print(retriever.invoke("我养了一只猫，叫笨笨"))

collection = db._collection  # 获取collection对象，可以直接使用collection对象进行操作

client.close()

from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain_community.vectorstores import FAISS

embedding = QianfanEmbeddingsEndpoint()

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
    {"page": 6},
    {"page": 7},
    {"page": 8},
    {"page": 9},
    {"page": 10},
]

db = FAISS.from_texts(
    texts,
    embedding,
    metadatas,
    relevance_score_fn=lambda distance: 1.0 / (1.0 + distance),
)

# print(f"总条数: {db.index.ntotal}")
# print("===========================================")

# print(db.similarity_search_with_scores("我养了一只猫，叫笨笨", filter=lambda x: x["page"] > 5))
# print("===========================================")
# print(
#     db.similarity_search_with_relevance_scores(
#         "我养了一只猫，叫笨笨", filter={"page": 10}
#     )
# )
# print("===========================================")
# print("获取ID")
# print(db.index_to_docstore_id)

# print("===========================================")
# # 根据ID删除
# db.delete([db.index_to_docstore_id[0]])
# print(f"总条数: {db.index.ntotal}")

# print("===========================================")
# # 添加新的文本
# ids = db.add_texts(["笨笨已经是一只7岁的猫了"])
# print("ids", ids)
# print(f"总条数: {db.index.ntotal}")

print("===========================================")
# 持久化
store_path = "./study/19-Faiss向量数据库/vector-store/"
db.save_local(store_path)

new_db = FAISS.load_local(store_path, embedding, allow_dangerous_deserialization=True)
print(new_db.similarity_search_with_score("我养了一只猫，叫笨笨"))

from dotenv import load_dotenv
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
import numpy as np
from numpy.linalg import norm

load_dotenv()


def cosine_similarity(vec1: list, vec2: list) -> float:
    # 计算余弦相似度
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = norm(vec1)
    norm_vec2 = norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)


embedding = QianfanEmbeddingsEndpoint()

query_vector = embedding.embed_query("我叫Leslie，我喜欢打篮球")
print(query_vector)
print(len(query_vector))

documents_vector = embedding.embed_documents(
    ["我叫Leslie，我喜欢打篮球", "这个喜欢打篮球的人，叫Leslie", "求知若渴，虚心若愚"]
)
print(len(documents_vector))
# 语义相同的句子，角度小，余弦相似度较高
# 0.9308035926342565
print(
    f"向量1和向量2的余弦相似度为：{cosine_similarity(documents_vector[0], documents_vector[1])}"
)
# 0.1246831215766497
print(
    f"向量1和向量3的余弦相似度为：{cosine_similarity(documents_vector[0], documents_vector[2])}"
)

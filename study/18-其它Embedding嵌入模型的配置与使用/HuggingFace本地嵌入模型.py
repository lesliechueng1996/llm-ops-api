from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="./study/18-其它Embedding嵌入模型的配置与使用/embeddings/",
)

query_vector = embedding.embed_query("我是Leslie，我喜欢打篮球")
print(query_vector)
print(len(query_vector))

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings

load_dotenv()

embedding = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

query_vector = embedding.embed_query("我是Leslie，我喜欢打篮球")
print(query_vector)
print(len(query_vector))

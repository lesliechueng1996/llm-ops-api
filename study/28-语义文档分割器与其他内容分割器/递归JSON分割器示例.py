from langchain_text_splitters import RecursiveJsonSplitter
import requests

url = "https://api.smith.langchain.com/openapi.json"
json_data = requests.get(url).json()

json_splitter = RecursiveJsonSplitter(max_chunk_size=300)
json_chunks = json_splitter.split_json(json_data)
chunks = json_splitter.create_documents(json_chunks)

print(len(chunks))

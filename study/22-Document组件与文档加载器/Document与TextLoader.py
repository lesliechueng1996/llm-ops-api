from langchain_community.document_loaders import TextLoader

loader = TextLoader(
    file_path="./study/22-Document组件与文档加载器/电商产品数据.txt",
    encoding="utf-8",
)

docs = loader.load()

print(len(docs))
print(docs[0].metadata)

from langchain_community.document_loaders import UnstructuredURLLoader

url_loader = UnstructuredURLLoader(
    urls=["https://www.imooc.com/"],
)

docs = url_loader.load()
print(docs)
print(len(docs))
print(docs[0].metadata)

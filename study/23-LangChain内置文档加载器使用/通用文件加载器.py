from langchain_unstructured.document_loaders import UnstructuredLoader

loader = UnstructuredLoader("./study/23-LangChain内置文档加载器使用/章节介绍.pptx")

docs = loader.load()

print(docs)
print(len(docs))
print(docs[0].metadata)

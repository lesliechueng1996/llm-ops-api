# from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader

# url_loader = UnstructuredURLLoader(
#     urls=["https://www.imooc.com/"],
# )
html_loader = UnstructuredHTMLLoader(
    file_path="./study/23-LangChain内置文档加载器使用/abc.html",
)


docs = html_loader.load()
print(docs)
print(len(docs))
print(docs[0].metadata)

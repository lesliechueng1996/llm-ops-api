from langchain_community.document_loaders import UnstructuredMarkdownLoader

# import nltk
# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context


# nltk.download("punkt")
# nltk.download("averaged_perceptron_tagger")

loader = UnstructuredMarkdownLoader(
    # file_path="./study/23-LangChain内置文档加载器使用/项目API资料.md",
    file_path="./study/23-LangChain内置文档加载器使用/a5f9f4ef-ae75-4333-8feb-95ce38b51a56.md",
)

docs = loader.load()
print(len(docs))

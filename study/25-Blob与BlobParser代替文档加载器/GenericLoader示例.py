from langchain_community.document_loaders.generic import GenericLoader

loader = GenericLoader.from_filesystem(
    path="./study/24-自定义加载器/", glob="*.txt", show_progress=True
)

for idx, doc in enumerate(loader.load()):
    print(f"第{idx}个文档为: {doc.metadata.get('source')}")

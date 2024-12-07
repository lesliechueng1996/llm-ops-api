from langchain_community.document_loaders.blob_loaders import FileSystemBlobLoader

loader = FileSystemBlobLoader(
    path="./study/25-Blob与BlobParser代替文档加载器/", glob="*.py", show_progress=True
)

for blob in loader.yield_blobs():
    print(blob.as_string())

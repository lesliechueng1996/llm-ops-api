from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
)

# excel_loader = UnstructuredExcelLoader(
#     file_path="./study/23-LangChain内置文档加载器使用/员工考勤表.xlsx",
# )
# docs = excel_loader.load()

# word_loader = UnstructuredWordDocumentLoader(
#     file_path="./study/23-LangChain内置文档加载器使用/喵喵.docx",
# )
# docs = word_loader.load()

ppt_loader = UnstructuredPowerPointLoader(
    file_path="./study/23-LangChain内置文档加载器使用/章节介绍.pptx",
)
docs = ppt_loader.load()

print(len(docs))
print(docs[0].metadata)
print(docs[0].page_content)

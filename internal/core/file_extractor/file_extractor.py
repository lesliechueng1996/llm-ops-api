"""
@Time   : 2024/12/18 13:26
@Author : Leslie
@File   : file_extractor.py
"""

from dataclasses import dataclass
import tempfile
from pathlib import Path
from injector import inject
import requests
from internal.model import UploadFile
from typing import Union
from langchain_core.documents import Document
from os import path
from internal.service import CosService
from langchain_community.document_loaders import (
    UnstructuredExcelLoader,
    UnstructuredPDFLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
    UnstructuredCSVLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredXMLLoader,
    TextLoader,
)
from langchain_unstructured.document_loaders import UnstructuredLoader


@inject
@dataclass
class FileExtractor:
    cos_service: CosService

    def load(
        self,
        upload_file: UploadFile,
        return_text: bool = False,
        is_unstructured: bool = True,
    ) -> Union[str, list[Document]]:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = path.join(temp_dir, path.basename(upload_file.key))
            self.cos_service.download_file(upload_file.key, file_path)
            return self.load_from_file(file_path, return_text, is_unstructured)

    def load_from_url(
        self, url: str, return_text: bool = False
    ) -> Union[list[Document], str]:
        """从传入的URL中去加载数据，返回LangChain文档列表或者字符串"""
        # 1.下载远程URL的文件到本地
        response = requests.get(url)

        # 2.将文件下载到本地的临时文件夹
        with tempfile.TemporaryDirectory() as temp_dir:
            # 3.获取文件的扩展名，并构建临时存储路径，将远程文件存储到本地
            file_path = path.join(temp_dir, path.basename(url))
            with open(file_path, "wb") as file:
                file.write(response.content)

            return self.load_from_file(file_path, return_text)

    def load_from_file(
        self, file_path: str, return_text: bool = False, is_unstructured: bool = True
    ) -> Union[str, list[Document]]:
        file_ext = Path(file_path).suffix.lower()

        if file_ext in [".xlsx", ".xls"]:
            loader = UnstructuredExcelLoader(file_path)
        elif file_ext == ".pdf":
            loader = UnstructuredPDFLoader(file_path)
        elif file_ext in [".md", ".markdown"]:
            loader = UnstructuredMarkdownLoader(file_path)
        elif file_ext in [".htm", ".html"]:
            loader = UnstructuredHTMLLoader(file_path)
        elif file_ext == ".csv":
            loader = UnstructuredCSVLoader(file_path)
        elif file_ext in [".ppt", ".pptx"]:
            loader = UnstructuredPowerPointLoader(file_path)
        elif file_ext in [".doc", ".docx"]:
            loader = UnstructuredWordDocumentLoader(file_path)
        elif file_ext == ".xml":
            loader = UnstructuredXMLLoader(file_path)
        elif not is_unstructured:
            loader = TextLoader(file_path)
        else:
            loader = UnstructuredLoader(file_path)

        docs = loader.load()
        if return_text:
            return "\n\n".join([doc.page_content for doc in docs])
        return docs

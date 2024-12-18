"""
@Time   : 2024/12/18 20:23
@Author : Leslie
@File   : document_handler.py
"""

from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.schema import CreateDocumentsSchemaReq
from pkg.response import validate_error_json, success_json


@inject
@dataclass
class DocumentHandler:
    def create_documents(self, dataset_id: UUID):
        req = CreateDocumentsSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)

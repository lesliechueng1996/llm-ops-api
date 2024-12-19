"""
@Time   : 2024/12/18 20:23
@Author : Leslie
@File   : document_handler.py
"""

from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.schema import CreateDocumentsSchemaReq, CreateDocumentsSchemaRes
from pkg.response import validate_error_json, success_json
from internal.service import DocumentService


@inject
@dataclass
class DocumentHandler:
    document_service: DocumentService

    def create_documents(self, dataset_id: UUID):
        req = CreateDocumentsSchemaReq()
        if not req.validate():
            return validate_error_json(req.errors)

        documents, batch = self.document_service.create_documents(
            dataset_id=dataset_id,
            upload_file_ids=req.upload_file_ids.data,
            process_type=req.process_type.data,
            rule=req.rule.data,
        )

        schema = CreateDocumentsSchemaRes()
        return success_json(schema.dump((documents, batch)))

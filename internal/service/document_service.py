"""
@Time   : 2024/12/18 20:26
@Author : Leslie
@File   : document_service.py
"""

import logging
from injector import inject
from dataclasses import dataclass
from pkg.sqlalchemy import SQLAlchemy
from internal.schema import CreateDocumentsSchemaReq
from internal.model import Document, Dataset, UploadFile, ProcessRule
from internal.exception import NotFoundException, FailException
from internal.entity import ALLOWED_DOCUMENT_EXTENSIONS, ProcessType
import time
import random


@inject
@dataclass
class DocumentService:
    db: SQLAlchemy

    def create_documents(
        self,
        dataset_id: str,
        upload_file_ids: list[str],
        process_type: str = ProcessType.AUTOMATIC,
        rule: dict = {},
    ) -> tuple[list[Document], str]:
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        # 校验数据集是否存在
        dataset = (
            self.db.session.query(Dataset)
            .filter(Dataset.id == dataset_id, Dataset.account_id == account_id)
            .get()
        )
        if not dataset:
            raise NotFoundException("数据集不存在")

        # 校验上传文件
        upload_files = (
            self.db.session.query(UploadFile)
            .filter(
                UploadFile.account_id == account_id,
                UploadFile.id.in_(upload_file_ids),
            )
            .all()
        )

        allowed_upload_files = [
            file
            for file in upload_files
            if file.extension.lower() in ALLOWED_DOCUMENT_EXTENSIONS
        ]
        if len(allowed_upload_files) == 0:
            logging.warning(
                f"上传文档列表未解析到合法文件，account_id: {account_id}, dataset_id: {dataset_id}, upload_file_ids: {upload_file_ids}"
            )
            raise FailException("暂未解析到合法文件，请重新上传")

        # 创建批次
        with self.db.auto_commit:
            batch = time.strftime("%Y%m%d%H%M%S") + str(random.randint(100000, 999999))
            process_rule = ProcessRule(
                account_id=account_id,
                dataset_id=dataset_id,
                mode=process_type,
                rule=rule,
            )

            start_position = self.get_latest_document_position(dataset_id=dataset_id)

            documents = []
            for upload_file in allowed_upload_files:
                start_position += 1
                document = Document(
                    account_id=account_id,
                    dataset_id=dataset_id,
                    upload_file_id=upload_file.id,
                    process_rule_id=process_rule.id,
                    batch=batch,
                    name=upload_file.name,
                    position=start_position,
                )
                documents.append(document)

            self.db.session.add_all(documents)

        return documents, batch

    def get_latest_document_position(self, dataset_id: str) -> int:
        last_document = (
            self.db.session.query(Document)
            .filter(Document.dataset_id == dataset_id)
            .order_by(Document.position.desc())
            .first()
        )
        return last_document.position if last_document else 0

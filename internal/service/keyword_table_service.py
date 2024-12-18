"""
@Time   : 2024/12/19 03:57
@Author : Leslie
@File   : keyword_table_service.py
"""

from injector import inject
from dataclasses import dataclass
from pkg.sqlalchemy import SQLAlchemy
from internal.model import KeywordTable


@inject
@dataclass
class KeywordTableService:
    db: SQLAlchemy

    def get_keyword_table_from_dataset_id(self, dataset_id: str) -> KeywordTable:
        record = (
            self.db.session.query(KeywordTable)
            .filter(KeywordTable.dataset_id == dataset_id)
            .one_or_none()
        )
        if record is None:
            record = KeywordTable(
                dataset_id=dataset_id,
                keyword_table={},
            )
            with self.db.auto_commit():
                self.db.session.add(record)
        return record

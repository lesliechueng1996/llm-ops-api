"""
@Time   : 2024/12/19 03:57
@Author : Leslie
@File   : keyword_table_service.py
"""

import logging
from uuid import UUID
from injector import inject
from dataclasses import dataclass
from redis import Redis
from pkg.sqlalchemy import SQLAlchemy
from internal.model import KeywordTable
from internal.entity import LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE, LOCK_EXPIRE_TIME


@inject
@dataclass
class KeywordTableService:
    db: SQLAlchemy
    redis_client: Redis

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

    def delete_keyword_table_from_ids(self, dataset_id: UUID, segment_ids: list[UUID]):
        lock_key = LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE.format(dataset_id=dataset_id)
        with self.redis_client.lock(lock_key, LOCK_EXPIRE_TIME):
            logging.info(f"获取锁 {lock_key}")

            keyword_table = self.get_keyword_table_from_dataset_id(dataset_id)
            all_keyword_table_map = keyword_table.keyword_table
            logging.info(
                f"before delete keyword table count: {len(all_keyword_table_map)}, dataset_id: {dataset_id}"
            )
            remaining_keyword_table_map = {}

            deleted_segment_ids = set([str(segment_id) for segment_id in segment_ids])

            for keyword, ids in all_keyword_table_map.items():
                ids_set = set(ids)
                if ids_set.intersection(deleted_segment_ids):
                    diff_ids = ids_set.difference(deleted_segment_ids)
                    if len(diff_ids) > 0:
                        remaining_keyword_table_map[keyword] = list(diff_ids)
                else:
                    remaining_keyword_table_map[keyword] = ids

            logging.info(
                f"After delete keyword table count: {len(remaining_keyword_table_map)}, dataset_id: {dataset_id}"
            )
            with self.db.auto_commit():
                keyword_table.keyword_table = remaining_keyword_table_map

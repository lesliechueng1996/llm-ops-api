"""
@Time   : 2024/12/21 17:40
@Author : Leslie
@File   : segment_service.py
"""

from injector import inject
from dataclasses import dataclass
from pkg.sqlalchemy import SQLAlchemy
from internal.schema import GetSegmentsPaginationSchemaReq
from pkg.pagination import Paginator
from internal.model import Segment
from sqlalchemy import asc


@inject
@dataclass
class SegmentService:
    db: SQLAlchemy

    def get_segments_pagination(
        self, dataset_id: str, document_id: str, req: GetSegmentsPaginationSchemaReq
    ):
        account_id = "46db30d1-3199-4e79-a0cd-abf12fa6858f"
        paginator = Paginator(self.db, req)

        filter = [
            Segment.dataset_id == dataset_id,
            Segment.document_id == document_id,
            Segment.account_id == account_id,
        ]

        if req.search_word.data:
            filter.append(Segment.content.ilike(f"%{req.search_word.data}%"))

        segments = paginator.paginate(
            self.db.session.query(Segment)
            .filter(*filter)
            .order_by(asc(Segment.position))
        )

        return segments, paginator

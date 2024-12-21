"""
@Time   : 2024/12/21 17:03
@Author : Leslie
@File   : segment_handler.py
"""

from uuid import UUID
from flask import request
from injector import inject
from dataclasses import dataclass
from internal.schema import (
    GetSegmentsPaginationSchemaReq,
    GetSegmentsPaginationItemSchemaRes,
)
from internal.exception import ValidateErrorException
from internal.service import SegmentService
from pkg.response import success_json
from pkg.pagination import PageModel


@inject
@dataclass
class SegmentHandler:
    segment_service: SegmentService

    def get_segments_pagination(self, dataset_id: UUID, document_id: UUID):
        req = GetSegmentsPaginationSchemaReq(request.args)
        if not req.validate():
            return ValidateErrorException(req.errors)

        segments, paginator = self.segment_service.get_segments_pagination(
            dataset_id=dataset_id, document_id=document_id, req=req
        )
        schema = GetSegmentsPaginationItemSchemaRes(many=True)
        return success_json(PageModel(schema.dump(segments), paginator))

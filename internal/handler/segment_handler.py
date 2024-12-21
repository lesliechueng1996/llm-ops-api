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
    GetSegmentSchemaRes,
    UpdateSegmentEnabledSchemaReq,
    CreateSegmentSchemaReq,
    UpdateSegmentSchemaReq,
)
from internal.exception import ValidateErrorException
from internal.service import SegmentService
from pkg.response import success_json, success_message
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

    def get_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        segment = self.segment_service.get_segment(
            dataset_id=dataset_id, document_id=document_id, segment_id=segment_id
        )
        schema = GetSegmentSchemaRes()
        return success_json(schema.dump(segment))

    def update_segment_enabled(
        self, dataset_id: UUID, document_id: UUID, segment_id: UUID
    ):
        req = UpdateSegmentEnabledSchemaReq()
        if not req.validate():
            return ValidateErrorException(req.errors)

        self.segment_service.update_segment_enabled(
            str(dataset_id), str(document_id), str(segment_id), req.enabled.data
        )
        return success_message("更新成功")

    def create_segment(self, dataset_id: UUID, document_id: UUID):
        req = CreateSegmentSchemaReq()
        if not req.validate():
            return ValidateErrorException(req.errors)

        self.segment_service.create_segment(str(dataset_id), str(document_id), req)
        return success_message("创建成功")

    def update_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        req = UpdateSegmentSchemaReq()
        if not req.validate():
            return ValidateErrorException(req.errors)

        self.segment_service.update_segment(
            str(dataset_id), str(document_id), str(segment_id), req
        )
        return success_message("更新成功")

    def delete_segment(self, dataset_id: UUID, document_id: UUID, segment_id: UUID):
        self.segment_service.delete_segment(
            str(dataset_id), str(document_id), str(segment_id)
        )
        return success_message("删除成功")

"""
@Time   : 2024/12/19 02:25
@Author : Leslie
@File   : document_task.py
"""

from celery import shared_task
from uuid import UUID


@shared_task
def build_documents(document_ids: list[UUID]):
    from app.http.module import injector
    from internal.service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.build_documents(document_ids)

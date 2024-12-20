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


@shared_task
def update_document_enabled(
    document_id: UUID, lock_key: str, lock_value: str, enabled: bool
):
    from app.http.module import injector
    from internal.service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.update_document_enabled(document_id, lock_key, lock_value, enabled)


@shared_task
def delete_document(dataset_id: UUID, document_id: UUID):
    from app.http.module import injector
    from internal.service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.delete_document(dataset_id, document_id)

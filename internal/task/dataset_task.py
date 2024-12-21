"""
@Time   : 2024/12/22 02:04
@Author : Leslie
@File   : dataset_task.py
"""

from celery import shared_task
from uuid import UUID


@shared_task
def delete_dataset(dataset_id: UUID):
    from app.http.module import injector
    from internal.service import IndexingService

    indexing_service = injector.get(IndexingService)
    indexing_service.delete_dataset(dataset_id)

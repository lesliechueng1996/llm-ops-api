"""
@Time   : 2024/12/17 21:20
@Author : Leslie
@File   : demo_task.py
"""

import logging
import time
from uuid import UUID
from celery import shared_task
from flask import current_app


@shared_task
def demo_task(id: UUID) -> str:
    logging.info("Sleeping for 5 seconds")
    time.sleep(5)
    logging.info(f"id: {id}")
    logging.info(f"config info: {current_app.config}")

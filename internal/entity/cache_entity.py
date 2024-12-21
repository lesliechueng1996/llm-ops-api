"""
@Time   : 2024/12/20 21:04
@Author : Leslie
@File   : cache_entity.py
"""

LOCK_DOCUMENT_UPDATE_ENABLED = "lock:document:update:enabled_{document_id}"

LOCK_KEYWORD_TABLE_UPDATE_KEYWORD_TABLE = (
    "lock:keyword_table:update:keyword_table_{dataset_id}"
)

LOCK_EXPIRE_TIME = 600

LOCK_SEGMENT_UPDATE_ENABLED = "lock:segment:update:enabled_{segment_id}"

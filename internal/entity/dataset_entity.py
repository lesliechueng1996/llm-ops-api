"""
@Time   : 2024/12/18 19:48
@Author : Leslie
@File   : dataset_entity.py
"""

from enum import Enum

DEFAULT_DATASET_DESCRIPTION_FORMATTER = (
    "当你需要回答管理《{name}》的时候可以引用该知识库。"
)


class ProcessType(str, Enum):
    AUTOMATIC = "automatic"
    CUSTOM = "custom"


DEFAULT_PROCESS_RULE = {
    "mode": "custom",
    "rule": {
        "pre_process_rules": [
            {"id": "remove_extra_space", "enabled": True},
            {"id": "remove_url_and_email", "enabled": True},
        ],
        "segment": {
            "separators": [
                "\n\n",
                "\n",
                "。|！|？",
                "\.\s|\!\s|\?\s",  # 英文标点符号后面通常需要加空格
                "；|;\s",
                "，|,\s",
                " ",
                "",
            ],
            "chunk_size": 500,
            "chunk_overlap": 50,
        },
    },
}


class DocumentStatus(str, Enum):
    WAITING = "waiting"
    PARSING = "parsing"
    SPLITTNG = "splitting"
    INDEXING = "indexing"
    COMPLETED = "completed"
    ERROR = "error"


class SegmentStatus(str, Enum):
    WAITING = "waiting"
    INDEXING = "indexing"
    COMPLETED = "completed"
    ERROR = "error"
